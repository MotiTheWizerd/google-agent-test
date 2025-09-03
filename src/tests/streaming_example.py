"""
Streaming example demonstrating real-time output from the agents manager.
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modules.core.agents_manager import AgentsManager


def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': Latest information about {query} as of 2025."


async def streaming_example():
    """Demonstrate streaming functionality."""
    print("=== Streaming Example ===\n")
    
    # Create agents manager
    manager = AgentsManager(app_name="streaming_example_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create a research workflow
    builder = manager.create_workflow_builder("research_assistant")
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="""You are a research assistant that explains topics in detail. 
        When asked about a topic, provide a comprehensive explanation with examples.
        Use the web_search tool when you need current information.
        Structure your response with clear sections and explanations.""",
        tools=["web_search"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("researcher").build()
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("research_assistant")
    
    print("\n" + "="*60)
    print("Streaming Research Assistant")
    print("="*60)
    
    # Example 1: Simple question
    print("\n📝 Example 1: Simple Question")
    print("-"*30)
    print("Question: Explain machine learning in simple terms\n")
    
    try:
        async for event in manager.stream_workflow(
            workflow_name="research_assistant",
            input_text="Explain machine learning in simple terms",
            user_id="researcher_001",
            session_id="session_001"
        ):
            # The streaming is handled by the executor, but we can still process events
            pass
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    
    # Example 2: Complex question with tool usage
    print("\n📝 Example 2: Complex Question with Tool Usage")
    print("-"*40)
    print("Question: What are the latest developments in quantum computing?\n")
    
    try:
        async for event in manager.stream_workflow(
            workflow_name="research_assistant",
            input_text="What are the latest developments in quantum computing?",
            user_id="researcher_002",
            session_id="session_002"
        ):
            # The streaming is handled by the executor, but we can still process events
            pass
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Streaming Example Completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(streaming_example())