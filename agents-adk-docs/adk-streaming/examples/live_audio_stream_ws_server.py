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