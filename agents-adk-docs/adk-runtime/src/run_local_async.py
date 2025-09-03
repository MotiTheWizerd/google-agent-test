import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents.root_agent import root_agent

APP_NAME = "adk-runtime-starter"
USER_ID = "user123"
SESSION_ID = "session-1"

async def main(query: str):
    # Create in-memory session + runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=query)])

    print("→ Streaming events:")
    events = runner.run_async(user_id=USER_ID, session_id=session.id, new_message=content)
    async for event in events:
        # Print streaming text as it arrives
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(text, end="", flush=True)

        if getattr(event, "is_final_response", None) and event.is_final_response():
            print("\n[final]\n")
            # You could also inspect event.actions.state_delta / artifact_delta here.

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "my name is Moti"
    asyncio.run(main(q))
