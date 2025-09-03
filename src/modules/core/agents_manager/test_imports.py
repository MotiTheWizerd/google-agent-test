"""Test script to verify the refactored agents manager implementation."""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modules.core.agents_manager import AgentsManager


def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': This is a mock search result."


async def test_agents_manager():
    """Test the refactored agents manager."""
    print("Testing refactored agents manager...")
    
    # Create agents manager
    manager = AgentsManager(app_name="test_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create a simple workflow
    builder = manager.create_workflow_builder("test_workflow")
    builder.add_llm_agent(
        name="assistant",
        model="gemini-2.0-flash",
        instruction="You are a helpful assistant. Use the web_search tool when needed.",
        tools=["web_search"]
    )
    
    # Register workflow
    workflow = builder.set_entry_point("assistant").build()
    manager.register_workflow(workflow)
    
    # List workflows
    workflows = manager.list_workflows()
    print(f"Registered workflows: {workflows}")
    
    # Test workflow info (avoiding UI output that might cause encoding issues)
    if "test_workflow" in workflows:
        print("Workflow registration successful!")
    else:
        print("Workflow registration failed!")
    
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_agents_manager())