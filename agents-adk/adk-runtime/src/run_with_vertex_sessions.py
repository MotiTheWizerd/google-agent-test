"""
Skeleton showing how to run with Vertex AI Agent Engine sessions.
You must set up GCP auth and install the extra dependencies:
    pip install "google-adk[vertexai]" "google-cloud-aiplatform[adk,agent_engine]"
"""
from google.adk.sessions import VertexAiSessionService
from google.adk.runners import Runner
from google.genai import types
from agents.root_agent import root_agent

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
# app_name used here should be the Agent Engine (Reasoning Engine) resource name
APP_NAME = "projects/{}/locations/{}/reasoningEngines/{}".format(PROJECT_ID, LOCATION, "ENGINE_ID")
USER_ID = "user123"

async def run(query: str):
    session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION, agent_engine_id=APP_NAME)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

    content = types.Content(role="user", parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(text, end="", flush=True)
        if getattr(event, "is_final_response", None) and event.is_final_response():
            print("\n[final]\n")
