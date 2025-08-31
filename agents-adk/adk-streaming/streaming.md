# Streaming with ADK — Developer Guide

## 1) Quick mental model
ADK exposes a **live**, bidirectional loop:
- You start a live session with `Runner.run_live(...)`.
- You push **requests** into a `LiveRequestQueue` (text as `Content`, audio/video as realtime blobs).
- You iterate an **async event stream** coming back (partial text, audio frames, tool calls, turn complete).

## 2) Minimal setup

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\Activate.ps1)
pip install google-adk python-dotenv fastapi uvicorn
```

Set a Gemini key (AI Studio) or Vertex project in `.env` at your app root:

```env
# AI Studio
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_KEY

# —or— Vertex
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
```

> Voice/video streaming requires a **Gemini Live** model. Check model IDs in Google’s docs.

For local mic/camera tests in browsers, also set:

```bash
export SSL_CERT_FILE=$(python -m certifi)  # (PowerShell: $env:SSL_CERT_FILE = (python -m certifi))
```

## 3) Live text streaming in ~40 lines

```python
# examples/python/live_text_stream.py
import asyncio
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part

# A tiny agent (no tools needed for demo)
root_agent = Agent(
    name="streaming_demo",
    model="gemini-2.0-flash-live-001",   # pick a Live-capable model
    instruction="Answer concisely."
)

async def main():
    runner = InMemoryRunner(app_name="adk_streaming_demo", agent=root_agent)

    # Create a session (in-memory)
    session = await runner.session_service.create_session(
        app_name="adk_streaming_demo",
        user_id="demo-user",
    )

    # Choose TEXT streaming; AUDIO also supported
    run_config = RunConfig(response_modalities=["TEXT"])

    # Start live loop
    live_queue = LiveRequestQueue()
    live_events = runner.run_live(session=session,
                                  live_request_queue=live_queue,
                                  run_config=run_config)

    # Send a user message
    live_queue.send_content(content=Content(role="user",
                                            parts=[Part.from_text("Give me three facts about Mars, stream as you think.")]))

    # Read partial responses
    async for event in live_events:
        for cand in getattr(event, "candidates", []):
            for part in getattr(cand, "content", {}).parts or []:
                if getattr(part, "text", None) and getattr(event, "partial", False):
                    print(part.text, end="", flush=True)

        if getattr(event, "turn_complete", False):
            print("\n[turn complete]\n")
            break

if __name__ == "__main__":
    asyncio.run(main())
```

## 4) WebSockets: text+audio relay server

This is a minimal FastAPI server that:
- opens a live ADK session,
- streams agent events to the client via WebSocket,
- accepts client **text** (`mime_type="text/plain"`) or PCM **audio** (`mime_type="audio/pcm"`, base64).

```python
# examples/python/live_audio_stream_ws_server.py
import os, json, base64, asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.genai.types import Part, Content, Blob
from google.adk.agents import Agent

load_dotenv()
APP_NAME = "adk_ws_demo"

root_agent = Agent(
    name="voice_agent",
    model="gemini-2.0-flash-live-001",
    instruction="Reply quickly. Speak when in audio mode."
)

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)+"/static"), name="static")

async def start_session(is_audio: bool):
    runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id="user-1")
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])
    live_queue = LiveRequestQueue()
    live_events = runner.run_live(session=session, live_request_queue=live_queue, run_config=run_config)
    return live_events, live_queue

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    # query param: ?audio=true
    is_audio = (ws.query_params.get("audio") == "true")
    live_events, live_queue = await start_session(is_audio=is_audio)

    async def agent_to_client():
        async for event in live_events:
            # stream partial text
            for cand in getattr(event, "candidates", []):
                for part in getattr(cand, "content", {}).parts or []:
                    if getattr(part, "text", None) and getattr(event, "partial", False):
                        await ws.send_text(json.dumps({"mime_type":"text/plain","data":part.text}))
            # stream audio frames (Base64 PCM) if present
            for blob in getattr(event, "blobs", []):
                if getattr(blob, "mime_type", "") == "audio/pcm":
                    await ws.send_text(json.dumps({"mime_type":"audio/pcm","data":base64.b64encode(blob.data).decode()}))

    async def client_to_agent():
        while True:
            msg = await ws.receive_text()
            payload = json.loads(msg)
            mt, data = payload["mime_type"], payload["data"]
            if mt == "text/plain":
                live_queue.send_content(Content(role="user", parts=[Part.from_text(data)]))
            elif mt == "audio/pcm":
                live_queue.send_realtime(Blob(mime_type="audio/pcm", data=base64.b64decode(data)))
            else:
                raise ValueError(f"Unsupported mime_type: {mt}")

    await asyncio.gather(agent_to_client(), client_to_agent())

# Optional: serve a tiny static client for manual testing
@app.get("/")
def index():
    return FileResponse(os.path.dirname(__file__)+"/static/index.html")
```

Create a tiny `static/index.html` that opens a WS and sends/receives messages — or wire this to your own UI.


## 5) Streaming tools (async generator tools)

You can define **streaming tools** (async generators) that yield intermediate values; the agent can react to them in real time.

```python
# examples/python/streaming_tools_demo.py
import asyncio
from typing import AsyncGenerator
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.agents import LiveRequestQueue

async def monitor_stock(ticker: str) -> AsyncGenerator[str, None]:
    for price in [300, 400, 900, 500]:
        await asyncio.sleep(2)
        yield f"{ticker} -> {price}"

def stop_streaming(function_name: str):
    """Hook for stopping a streaming tool by name (implement your own registry)."""
    pass

root_agent = Agent(
    name="streaming_tools_agent",
    model="gemini-2.0-flash-live-001",
    instruction=(
        "Use monitor_stock to watch a ticker. Read its streamed values and speak when a price changes materially."
    ),
    tools=[monitor_stock, FunctionTool(stop_streaming)]
)

# You can now run this agent with run_live(...), ask it to 'monitor AAPL', and it will react as yields arrive.
```

**Rules**
- Tool must be `async def` and return `AsyncGenerator[T, None]`.
- For **video** streaming tools, accept a reserved `input_stream: LiveRequestQueue` parameter and poll latest frames.

## 6) Tuning streaming behavior
Use `RunConfig` for voice (speech), response modality, and resumption:

```python
from google.genai import types as genai_types
from google.adk.agents.run_config import RunConfig

voice = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name="Aoede")
)
speech = genai_types.SpeechConfig(voice_config=voice)

run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=speech,
    # session_resumption=genai_types.SessionResumptionConfig()
)
```

## 7) Notes & gotchas
- Live requires a **Live‑capable** Gemini model (e.g., `gemini-2.0-flash-live-*`). Verify exact IDs in the official docs.
- In browser voice/video, export `SSL_CERT_FILE` so the dev UI can capture devices.
- Some non‑live features (callbacks, long running tools) may be limited in current streaming builds; check the official “Note on ADK Streaming”.
- For production: prefer WebSockets over SSE for duplex audio; add sticky sessions or stateless design; monitor reconnects; secure endpoints.

