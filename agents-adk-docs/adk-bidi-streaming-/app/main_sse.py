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

APP_NAME = 'adk-bidi-sse'
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
sessions: dict[str, dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')), name='static')

def _parse_client_payload(payload: dict):
    return payload.get('type'), payload

@app.get('/events/{session_id}')
async def sse_events(session_id: str):
    if session_id not in sessions:
        session = await session_service.create_session(app_name=APP_NAME, user_id=session_id)
        queue = LiveRequestQueue()

        voice = genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name='Aoede'))
        speech = genai_types.SpeechConfig(voice_config=voice)
        config = RunConfig(speech_config=speech, response_modalities=['AUDIO','TEXT'])

        live_events = runner.run_live(session=session, live_request_queue=queue, run_config=config)
        sessions[session_id] = {'session': session, 'queue': queue, 'events': live_events}
    else:
        live_events = sessions[session_id]['events']

    async def event_source():
        async for event in live_events:
            data = json.dumps(event.to_dict() if hasattr(event, 'to_dict') else {'event': str(event)})
            yield f'data: {data}\n\n'
            await asyncio.sleep(0)
    return StreamingResponse(event_source(), media_type='text/event-stream')

@app.post('/send/{session_id}')
async def send_input(session_id: str, request: Request):
    if session_id not in sessions:
        return Response(status_code=404, content='unknown session')
    body = await request.json()
    kind, payload = _parse_client_payload(body)
    queue: LiveRequestQueue = sessions[session_id]['queue']

    if kind == 'text':
        await queue.send_content(payload.get('text') or '')
    elif kind == 'audio':
        b = base64.b64decode(payload['base64'])
        blob = genai_types.Blob(data=b, mime_type=payload.get('mime_type', 'audio/pcm'))
        await queue.send_realtime(blob)
    else:
        return Response(status_code=400, content='unknown type')
    return {'ok': True}

@app.get('/')
async def index():
    return Response(headers={'Location': '/static/index.html'}, status_code=307)
