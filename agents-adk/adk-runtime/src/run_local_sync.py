from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.root_agent import root_agent

APP_NAME = "adk-runtime-starter"
USER_ID = "user123"

def main(query: str):
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=query)])
    # Synchronous convenience method (internally uses async).
    for event in runner.run(user_id=USER_ID, session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(text, end="", flush=True)
        if getattr(event, "is_final_response", None) and event.is_final_response():
            print("\n[final]\n")

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "explain ADK runtime in one line"
    main(q)
