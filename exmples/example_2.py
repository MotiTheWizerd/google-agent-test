import asyncio
import json
from typing import Dict, Any
from dotenv import load_dotenv
from google.adk.agents import LlmAgent as Agent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Load environment variables
load_dotenv()

# Researcher agent that uses web search to gather information
researcher_agent = Agent(
    model="gemini-2.0-flash",
    name="researcher",
    description="Researches topics using web search",
    instruction=(
        "You are a research specialist. When given a topic, use the google_search tool "
        "to find relevant information. Focus on gathering key facts, recent developments, "
        "and important context about the topic. Save your findings in the session state "
        "under the key 'research_notes'. Be thorough but concise in your research notes."
    ),
    tools=[google_search],
    output_key="research_notes"
)

# Writer agent that creates a summary based on research
writer_agent = Agent(
    model="gemini-2.0-flash",
    name="writer",
    description="Writes summaries based on research",
    instruction=(
        "You are a skilled writer who creates clear, engaging summaries. "
        "Use the research notes provided to write a well-structured summary "
        "that covers the key points about the topic. Your summary should be "
        "informative yet accessible, about 3-4 paragraphs long. Include important "
        "facts, recent developments, and context. Make it engaging for a general audience."
    ),
    include_contents="default"  # Access to previous conversation including research notes
)

# Sequential agent that runs researcher then writer
research_and_write_agent = SequentialAgent(
    name="research_and_write",
    description="Researches a topic and writes a summary",
    sub_agents=[researcher_agent, writer_agent]
)

async def main():
    # Get topic from user
    topic = input("Enter a topic you'd like researched and summarized: ")
    
    if not topic.strip():
        print("No topic provided. Exiting.")
        return
    
    print(f"\nResearching and summarizing: {topic}")
    print("=" * 50)
    
    # Create runner and session
    runner = InMemoryRunner(agent=research_and_write_agent, app_name="research_app")
    session = await runner.session_service.create_session(
        app_name="research_app",
        user_id="research_user"
    )
    
    # Run the sequential agent
    message = types.Content(
        parts=[types.Part(text=f"Research and write a summary about: {topic}")], 
        role="user"
    )
    
    async for event in runner.run_async(
        user_id="research_user",
        session_id=session.id,
        new_message=message
    ):
        # Show tool calls
        if hasattr(event, 'get_function_calls'):
            for call in event.get_function_calls() or []:
                print(f"[Tool Call] {call.name}({call.args})")
        
        # Show tool responses
        if hasattr(event, 'get_function_responses'):
            for response in event.get_function_responses() or []:
                print(f"[Tool Response] Received search results")
        
        # Show researcher's notes
        if event.author == "researcher" and event.is_final_response() and event.content:
            print("\n--- Research Notes ---")
            print(event.content.parts[0].text)
            print("--- End Research Notes ---\n")
        
        # Show final summary
        if event.author == "writer" and event.is_final_response() and event.content:
            print("--- Summary ---")
            print(event.content.parts[0].text)
            print("--- End Summary ---\n")

if __name__ == "__main__":
    print("🔍 Research & Summary Agent 🔍")
    print("I'll research any topic and provide a well-written summary!")
    
    asyncio.run(main())
    
    print("\n📚 Thanks for using the Research & Summary Agent! 📚")