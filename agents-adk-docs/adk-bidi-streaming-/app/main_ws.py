import asyncio, base64, json, os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue, RunConfig
from google.genai import types as genai_types
from google_search_agent.agent import root_agent

APP_NAME = 'adk-bidi-ws'
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

app = FastAPI()
app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')), name='static')

@app.websocket('/ws/{session_id}')
async def ws_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        session = await session_service.create_session(app_name=APP_NAME, user_id=session_id)
        queue = LiveRequestQueue()

        voice = genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(voice_name='Aoede'))
        speech = genai_types.SpeechConfig(voice_config=voice)
        config = RunConfig(speech_config=speech, response_modalities=['AUDIO','TEXT'])

        live_events = runner.run_live(session=session, live_request_queue=queue, run_config=config)

        async def pump_events():
            async for event in live_events:
                payload = event.to_dict() if hasattr(event, 'to_dict') else {'event': str(event)}
                await ws.send_text(json.dumps(payload))

        async def pump_incoming():
            while True:
                msg = await ws.receive_text()
                data = json.loads(msg)
                if data.get('type') == 'text':
                    await queue.send_content(data.get('text') or '')
                elif data.get('type') == 'audio':
                    b = base64.b64decode(data['base64'])
                    blob = genai_types.Blob(data=b, mime_type=data.get('mime_type', 'audio/pcm'))
                    await queue.send_realtime(blob)

        await asyncio.gather(pump_events(), pump_incoming())
    except WebSocketDisconnect:
        pass
