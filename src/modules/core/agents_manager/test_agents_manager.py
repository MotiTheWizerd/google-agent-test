"""Test file to verify the agents manager module restructuring."""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager.agents_manager import AgentsManager
from modules.core.agents_manager.workflow_builder import WorkflowBuilder


def simple_tool(query: str) -> str:
    """A simple test tool."""
    return f"Tool response for: {query}"


async def test_agents_manager():
    """Test the agents manager functionality."""
    print("Testing Agents Manager...")
    
    # Create agents manager
    manager = AgentsManager(app_name="test_app")
    
    # Register a simple tool
    manager.register_tool("simple_tool", simple_tool)
    
    # Create a simple workflow
    builder = manager.create_workflow_builder("test_workflow")
    builder.add_llm_agent(
        name="test_agent",
        model="gemini-2.0-flash",
        instruction="You are a test assistant. Use the simple_tool when needed.",
        tools=["simple_tool"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("test_agent").build()
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("test_workflow")
    
    print("✅ Agents Manager test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_agents_manager())