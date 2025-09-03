import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from google.adk.agents import LlmAgent as Agent, LoopAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types

# Load environment variables
load_dotenv()

# Mock search tool that returns sample information
def mock_search(query: str) -> str:
    """Mock search tool that returns sample information based on the query."""
    mock_data = {
        "bitcoin": """Bitcoin (BTC) is a decentralized digital currency that operates without a central bank or single administrator.
It was invented by an unknown person or group of people using the name Satoshi Nakamoto and released as open-source software in 2009.
Bitcoin transactions are verified by network nodes through cryptography and recorded in a public distributed ledger called a blockchain.
Bitcoin is the first decentralized digital currency and the first cryptocurrency to solve the double-spending problem without requiring trusted authorities.
As of recent data, Bitcoin has a market cap of over $1 trillion and is the largest cryptocurrency by market capitalization.""",
        "artificial intelligence": """Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn.
AI can be categorized into narrow AI (designed for specific tasks) and general AI (capable of performing any intellectual task a human can do).
Recent advances in machine learning, particularly deep learning, have led to significant breakthroughs in areas like natural language processing, computer vision, and robotics.
Major tech companies like Google, Microsoft, and OpenAI are investing heavily in AI research and development.
Ethical considerations around AI include concerns about job displacement, bias in algorithms, and the potential for misuse.""",
        "climate change": """Climate change refers to long-term changes in temperatures and weather patterns, primarily caused by human activities.
The burning of fossil fuels releases greenhouse gases like carbon dioxide into the atmosphere, trapping heat and causing global warming.
The Paris Agreement, signed in 2015, aims to limit global warming to well below 2 degrees Celsius above pre-industrial levels.
Impacts of climate change include rising sea levels, more frequent extreme weather events, and shifts in ecosystems and wildlife populations.
Solutions include transitioning to renewable energy, improving energy efficiency, and implementing carbon pricing mechanisms."""
    }
    
    # Find the best match in the query
    query_lower = query.lower()
    for key, value in mock_data.items():
        if key in query_lower:
            return value
    
    # Default response if no match found
    return f"Search results for '{query}': This is a mock search result. In a real implementation, this would contain actual information about {query}."

# Researcher agent that uses mock search to gather information
researcher_agent = Agent(
    model="gemini-2.0-flash",
    name="researcher",
    description="Researches topics using mock search",
    instruction=(
        "You are a research specialist. When given a topic, use the mock_search tool "
        "to find relevant information. Focus on gathering key facts, recent developments, "
        "and important context about the topic. Save your findings in the session state "
        "under the key 'research_notes'. Be thorough but concise in your research notes."
    ),
    tools=[FunctionTool(mock_search)],
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
    output_key="draft_summary"
)

# Reviewer agent that evaluates the summary and provides feedback
reviewer_agent = Agent(
    model="gemini-2.0-flash",
    name="reviewer",
    description="Reviews summaries and provides feedback",
    instruction="""You are a critical reviewer who evaluates written content. 
Review the provided summary and assess its quality based on:
1. Accuracy - Are facts correct and well-supported?
2. Clarity - Is it well-organized and easy to understand?
3. Completeness - Does it cover key points adequately?
4. Engagement - Is it interesting for a general audience?

If the summary meets high standards, respond with exactly: 'APPROVED'
If improvements are needed, provide specific, actionable feedback on what to improve."""

)

# Custom agent to check if review is approved
class ReviewChecker(BaseAgent):
    def __init__(self):
        super().__init__(name="review_checker")
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Get the latest review from session state
        review = ctx.session.state.get("review_result", "")
        
        # Check if review is approved
        is_approved = "APPROVED" in review.upper()
        
        # Print debug info
        print(f"[Debug] Review content: '{review}'")
        print(f"[Debug] Is approved: {is_approved}")
        
        # Create event with escalation action if approved
        actions = EventActions(escalate=is_approved)
        
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Review check: {'Approved' if is_approved else 'Needs revision'}")], role="system"),
            actions=actions
        )

# Create the loop agent that repeats writer->reviewer cycle until approved or max iterations
review_loop_agent = LoopAgent(
    name="review_loop",
    description="Writes and reviews summaries until approved or max iterations reached",
    sub_agents=[writer_agent, reviewer_agent, ReviewChecker()],
    max_iterations=5
)

# Main agent that orchestrates the full flow: research -> write/review loop
research_review_agent = Agent(
    model="gemini-2.0-flash",  # Added model to fix the error
    name="research_review_orchestrator",
    description="Researches a topic and writes a summary with review cycles",
    sub_agents=[researcher_agent, review_loop_agent]
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
    runner = InMemoryRunner(agent=research_review_agent, app_name="research_review_app")
    session = await runner.session_service.create_session(
        app_name="research_review_app",
        user_id="research_user"
    )
    
    # Run the agent
    message = types.Content(
        parts=[types.Part(text=f"Research and write a summary about: {topic}")], 
        role="user"
    )
    
    iteration = 0
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
                print(f"[Tool Response] {response.response}")
        
        # Show researcher's notes
        if event.author == "researcher" and event.is_final_response() and event.content:
            print("\n--- Research Notes ---")
            print(event.content.parts[0].text)
            print("--- End Research Notes ---\n")
        
        # Show draft summaries
        if event.author == "writer" and event.is_final_response() and event.content:
            iteration += 1
            print(f"--- Draft Summary (Iteration {iteration}) ---")
            print(event.content.parts[0].text)
            print("--- End Draft Summary ---\n")
        
        # Show reviews
        if event.author == "reviewer" and event.is_final_response() and event.content:
            review_text = event.content.parts[0].text
            print("--- Review ---")
            print(review_text)
            # Store review in session state for the checker
            session.state["review_result"] = review_text
            print("--- End Review ---\n")
        
        # Show final approved summary
        if event.author == "review_loop" and event.is_final_response() and event.content:
            print("--- Final Approved Summary ---")
            print(event.content.parts[0].text)
            print("--- End Final Summary ---\n")
            
        # Show when loop is complete
        if event.author == "review_checker":
            if "Approved" in str(event.content.parts[0].text):
                print("✅ Summary approved by reviewer!")
            else:
                print("🔄 Summary needs revision...")

if __name__ == "__main__":
    print("🔍 Research & Review Agent 🔍")
    print("I'll research any topic, write a summary, and iterate until it's perfect!")
    
    asyncio.run(main())
    
    print("\n📚 Thanks for using the Research & Review Agent! 📚")