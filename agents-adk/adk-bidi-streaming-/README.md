# Google ADK — Bidi‑Streaming Developer Guide (Python)

This mini‑project shows how to build **bidirectional streaming** (voice/video/text in — streamed agent events out) using the Google **Agent Development Kit (ADK)**, with both **SSE** and **WebSockets** server patterns and minimal client snippets.

> Works locally with `google-adk` and FastAPI. You can swap to Vertex AI later without changing app logic.

## What you get

- `app/google_search_agent/agent.py` — a minimal streaming‑ready agent.
- `app/main_sse.py` — FastAPI + **SSE** server.
- `app/main_ws.py` — FastAPI + **WebSockets** server.
- `app/static/index.html` + `app/static/client_ws.js` — tiny browser client for WebSockets.
- `requirements.txt` — deps.

## 1) Install

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `app/.env` with either **AI Studio** or **Vertex** credentials:

**AI Studio (local API key)**
```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_API_KEY
```

**Vertex AI (project / location)**
```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

> For microphone/video in browsers on some platforms, set SSL cert bundle for the Python process:
>
> **Linux/macOS:** `export SSL_CERT_FILE=$(python -m certifi)`  
> **Windows PowerShell:** `$env:SSL_CERT_FILE = (python -m certifi)`

## 2) Project layout

```
adk-bidi-streaming-starter/
└─ app/
   ├─ .env
   ├─ main_sse.py
   ├─ main_ws.py
   ├─ static/
   │  ├─ index.html
   │  └─ client_ws.js
   └─ google_search_agent/
      ├─ __init__.py
      └─ agent.py
```

## 3) The agent

`Agent` is standard ADK; the **same agent** works for streaming and non‑streaming. You only need a model that supports the **Gemini Live API** and any tools you want.

```python
# app/google_search_agent/agent.py
from google.adk.agents import Agent
from google.adk.tools import google_search  # built-in grounding tool

# Check docs for the latest Live model ids (e.g. "gemini-2.0-flash-live-001").
root_agent = Agent(
    name="basic_search_agent",
    model="gemini-2.0-flash-live-001",
    description="Answers with grounded facts via Google Search.",
    instruction="You are an expert researcher. Be concise and factual.",
    tools=[google_search],
)
```

## 4) Run an SSE server

This pattern exposes:
- `GET /events/{session_id}`: SSE stream of agent events to the browser.
- `POST /send/{session_id}`: send user input (text or audio) **to** the agent.

```python
# app/main_sse.py
import asyncio, base64, json, os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue, RunConfig
from google.genai import types as genai_types
from google_search_agent.agent import root_agent

APP_NAME = "adk-bidi-sse"
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
sessions: dict[str, dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Any startup logic goes here
    yield
    # Any shutdown logic goes here

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

def _parse_client_payload(payload: dict):
    """Accepts {'type':'text'|'audio', ...}; returns a LiveRequestQueue sender call."""
    return payload.get("type"), payload

@app.get("/events/{session_id}")
async def sse_events(session_id: str):
    # Create or resume a session & live queue
    if session_id not in sessions:
        session = await session_service.create_session(app_name=APP_NAME, user_id=session_id)
        queue = LiveRequestQueue()
        # Optional voice config
        voice = genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name="Aoede"))
        speech = genai_types.SpeechConfig(voice_config=voice)
        config = RunConfig(speech_config=speech)
        live_events = runner.run_live(session=session, live_request_queue=queue, run_config=config)
        sessions[session_id] = {"session": session, "queue": queue, "events": live_events}
    else:
        live_events = sessions[session_id]["events"]

    async def event_source():
        async for event in live_events:
            # Minimal transport: forward event as JSON (you can filter/reshape).
            data = json.dumps(event.to_dict() if hasattr(event, "to_dict") else {"event": str(event)})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0)
    return StreamingResponse(event_source(), media_type="text/event-stream")

@app.post("/send/{session_id}")
async def send_input(session_id: str, request: Request):
    body = await request.json()
    kind, payload = _parse_client_payload(body)
    queue: LiveRequestQueue = sessions[session_id]["queue"]

    if kind == "text":
        # Send user text
        await queue.send_content(payload.get("text") or "")
    elif kind == "audio":
        # Expect base64 PCM16 mono 16k: {type: 'audio', mime_type: 'audio/pcm', base64: '...'}
        b = base64.b64decode(payload["base64"])
        blob = genai_types.Blob(data=b, mime_type=payload.get("mime_type", "audio/pcm"))
        await queue.send_realtime(blob)
    else:
        return Response(status_code=400, content="unknown type")
    return {"ok": True}

# dev helper landing page
@app.get("/")
async def index():
    return Response(headers={"Location": "/static/index.html"}, status_code=307)
```

Run it:
```bash
uvicorn app.main_sse:app --reload
```

Open http://127.0.0.1:8000/ and use a simple client to `POST /send` and subscribe to `/events`.

## 5) Run a WebSockets server

This pattern pushes events and accepts inputs on the same socket.

```python
# app/main_ws.py
import asyncio, base64, json, os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue, RunConfig
from google.genai import types as genai_types
from google_search_agent.agent import root_agent

APP_NAME = "adk-bidi-ws"
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.websocket("/ws/{session_id}")
async def ws_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        session = await session_service.create_session(app_name=APP_NAME, user_id=session_id)
        queue = LiveRequestQueue()

        # Optional voice config
        voice = genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name="Aoede"))
        speech = genai_types.SpeechConfig(voice_config=voice)
        config = RunConfig(speech_config=speech)

        # Start agent stream
        live_events = runner.run_live(session=session, live_request_queue=queue, run_config=config)

        async def pump_events():
            async for event in live_events:
                payload = event.to_dict() if hasattr(event, "to_dict") else {"event": str(event)}
                await ws.send_text(json.dumps(payload))

        async def pump_incoming():
            while True:
                msg = await ws.receive_text()
                data = json.loads(msg)
                if data.get("type") == "text":
                    await queue.send_content(data.get("text") or "")
                elif data.get("type") == "audio":
                    b = base64.b64decode(data["base64"])
                    blob = genai_types.Blob(data=b, mime_type=data.get("mime_type", "audio/pcm"))
                    await queue.send_realtime(blob)

        await asyncio.gather(pump_events(), pump_incoming())
    except WebSocketDisconnect:
        pass
```

Run it:
```bash
uvicorn app.main_ws:app --reload
```

Open http://127.0.0.1:8000/ to load the tiny WebSocket client.

## 6) Tiny WebSocket client

`app/static/index.html` serves a minimal page; `app/static/client_ws.js` connects, records the mic as PCM16, and streams as base64. This is intentionally tiny and **not** production‑grade.

```html
<!-- app/static/index.html -->
<!doctype html>
<html>
  <head><meta charset="utf-8"/><title>ADK WS Demo</title></head>
  <body>
    <h3>ADK Bidi‑Streaming (WebSocket)</h3>
    <input id="sid" placeholder="session id" value="user1"/>
    <button id="connect">Connect</button>
    <button id="say">Send Text</button>
    <button id="mic">Toggle Mic</button>
    <pre id="log"></pre>
    <script src="client_ws.js"></script>
  </body>
</html>
```

```js
// app/static/client_ws.js
const log = (...a) => (document.getElementById("log").textContent += a.join(" ") + "\n");

let ws, mediaStream, processor, audioCtx, micOn = false;

document.getElementById("connect").onclick = () => {
  const sid = document.getElementById("sid").value || "user1";
  ws = new WebSocket(`ws://${location.host}/ws/${encodeURIComponent(sid)}`);
  ws.onopen = () => log("ws open");
  ws.onerror = (e) => log("ws error", e.message || e);
  ws.onclose = () => log("ws closed");
  ws.onmessage = (e) => log("event:", e.data.slice(0, 200));
};

document.getElementById("say").onclick = () => {
  if (!ws || ws.readyState !== 1) return;
  const text = prompt("Say:");
  if (text) ws.send(JSON.stringify({ type: "text", text }));
};

document.getElementById("mic").onclick = async () => {
  if (!ws || ws.readyState !== 1) return;

  if (!micOn) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const source = audioCtx.createMediaStreamSource(mediaStream);
    const node = audioCtx.createScriptProcessor(4096, 1, 1);
    node.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      // Float32 [-1,1] -> PCM16
      const buf = new ArrayBuffer(input.length * 2);
      const view = new DataView(buf);
      for (let i = 0; i < input.length; i++) {
        let s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
      const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
      ws.send(JSON.stringify({ type: "audio", mime_type: "audio/pcm", base64: b64 }));
    };
    source.connect(node);
    node.connect(audioCtx.destination);
    processor = node;
    micOn = true;
    log("mic on");
  } else {
    processor?.disconnect();
    mediaStream?.getTracks().forEach(t => t.stop());
    await audioCtx?.close();
    micOn = false;
    log("mic off");
  }
};
```

## 7) Streaming Tools (optional)

You can define streaming tools that **yield** intermediate values and let the agent react in real time. Example skeletons:

```python
import asyncio
from typing import AsyncGenerator
from google.adk.agents import LiveRequestQueue
from google.genai import Client, types as genai_types
from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool

async def monitor_stock_price(ticker: str) -> AsyncGenerator[str, None]:
    # Replace with real feed. Demonstration: emit every few seconds.
    for px in (300, 400, 900, 500):
        await asyncio.sleep(4)
        yield f"price({ticker})={px}"

async def monitor_video_stream(input_stream: LiveRequestQueue) -> AsyncGenerator[str, None]:
    """Scan latest JPEG frames in the live input queue and emit a count change."""
    client = Client(vertexai=False)
    last = None
    while True:
        latest = None
        while input_stream._queue.qsize() != 0:  # pop most recent
            req = await input_stream.get()
            if req.blob and req.blob.mime_type == "image/jpeg":
                latest = req
        if latest:
            image_part = genai_types.Part.from_bytes(data=latest.blob.data, mime_type=latest.blob.mime_type)
            contents = genai_types.Content(role="user", parts=[image_part, genai_types.Part.from_text("Count people as a number.")])
            resp = client.models.generate_content(model="gemini-2.0-flash-exp", contents=contents)
            text = resp.candidates[0].content.parts[0].text
            if last != text:
                last = text
                yield f"people={text}"
        await asyncio.sleep(0.5)

def stop_streaming(function_name: str):  # stub for graceful stop signals
    pass

streaming_agent = Agent(
    model="gemini-2.0-flash-live-001",
    name="video_streaming_agent",
    instruction="Use tools to monitor video or prices. Speak only when you have a new update.",
    tools=[monitor_video_stream, monitor_stock_price, FunctionTool(stop_streaming)],
)
```

## 8) Common RunConfig knobs

```python
from google.adk.agents import RunConfig
from google.genai import types as genai_types

run_config = RunConfig(
    # Stream back audio + text
    response_modalities=["AUDIO", "TEXT"],
    # Voice config (prebuilt voice)
    speech_config=genai_types.SpeechConfig(
        voice_config=genai_types.VoiceConfig(
            prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name="Aoede")
        )
    ),
    # Proactive mode lets the agent speak up without waiting for text
    proactivity=True,
    # Realtime input (e.g., prefer server‑side downsampling/encoding)
    realtime_input_config=genai_types.RealtimeInputConfig(),
)
```

## 9) Try it

- **SSE:** `uvicorn app.main_sse:app --reload` and open `/` in a browser. Use your own client or curl to `POST /send`.
- **WebSockets:** `uvicorn app.main_ws:app --reload` and open `/`.

## 10) Notes & troubleshooting

- If you see microphone permission issues, check that the page is loaded from `http://localhost` (or serve via HTTPS for production).
- Ensure your **model id** supports **Live API**.
- For Windows terminals and voice, remember to set `SSL_CERT_FILE` as shown above.
- For production, persist sessions with `DatabaseSessionService` or `VertexAiSessionService`.

---

**License:** Public domain snippet pack. Replace keys and models with your own.
