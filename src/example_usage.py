"""Example usage of the agents manager module."""

import asyncio
import os
from dotenv import load_dotenv

# Add src to Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager, WorkflowBuilder


# Load environment variables
load_dotenv()


def get_current_weather(location: str) -> str:
    """Mock tool to get current weather."""
    return f"The weather in {location} is sunny with a temperature of 22°C (72°F)."

def search_web(query: str) -> str:
    """Mock tool to search the web."""
    return f"Search results for '{query}': This is a mock search result. In a real implementation, this would contain actual information about {query}."


async def main():
    """Main example function."""
    # Create agents manager
    manager = AgentsManager(app_name="example_app")
    
    # Register tools
    manager.register_tool("get_weather", get_current_weather)
    manager.register_tool("search_web", search_web)
    
    # Create a research workflow using the builder
    builder = manager.create_workflow_builder("research_workflow")
    builder.set_description("Research a topic and provide a summary")
    
    # Add a researcher agent
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="You are a research specialist. Use the search_web tool to find relevant information about the given topic. Focus on gathering key facts and recent developments. Save your findings in the session state under the key 'research_notes'.",
        tools=["search_web"],
        output_key="research_notes"
    )
    
    # Add a writer agent
    builder.add_llm_agent(
        name="writer",
        model="gemini-2.0-flash",
        instruction="You are a skilled writer who creates clear, engaging summaries. Use the research notes provided to write a well-structured summary that covers the key points about the topic. Your summary should be informative yet accessible, about 3-4 paragraphs long.",
        output_key="final_summary"
    )
    
    # Add a sequential agent to orchestrate the flow
    builder.add_sequential_agent(
        name="research_and_write",
        sub_agents=["researcher", "writer"]
    )
    
    # Set entry point and build
    workflow = builder.set_entry_point("research_and_write").build()
    
    # Register the workflow
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("research_workflow")
    
    # Run the workflow
    topic = "artificial intelligence trends in 2025"
    try:
        result = await manager.run_workflow(
            workflow_name="research_workflow",
            input_text=topic,
            user_id="user_001",
            session_id="session_001"
        )
        print("\nWorkflow completed successfully!")
        print(f"Final output: {result['final_output']}")
    except Exception as e:
        print(f"Error running workflow: {e}")


if __name__ == "__main__":
    print("🚀 Starting Agents Manager Example 🚀")
    asyncio.run(main())
    print("\n✅ Example completed!")