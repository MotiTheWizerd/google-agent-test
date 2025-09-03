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