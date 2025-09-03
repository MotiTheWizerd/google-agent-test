"""Multi-user example demonstrating the agents manager with proper session management."""

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
    """Main multi-user example function."""
    # Create agents manager
    manager = AgentsManager(app_name="multi_user_example_app")
    
    # Register tools
    manager.register_tool("get_weather", get_current_weather)
    manager.register_tool("search_web", search_web)
    
    # Create a weather assistant workflow
    builder = manager.create_workflow_builder("weather_assistant")
    builder.set_description("Weather assistant that provides weather information")
    
    # Add a weather agent
    builder.add_llm_agent(
        name="weather_agent",
        model="gemini-2.0-flash",
        instruction="You are a weather assistant. Use the get_weather tool to provide weather information for locations. Be friendly and helpful.",
        tools=["get_weather"],
        output_key="weather_info"
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("weather_agent").build()
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("weather_assistant")
    
    # Simulate multiple users using the system
    users = [
        {"user_id": "user_001", "session_id": "sess_001", "query": "What's the weather like in New York?"},
        {"user_id": "user_002", "session_id": "sess_002", "query": "How's the weather in London?"},
        {"user_id": "user_003", "session_id": "sess_003", "query": "What's the weather in Tokyo?"},
    ]
    
    # Run workflows for each user
    results = []
    for user in users:
        print(f"\n{'='*50}")
        print(f"Running workflow for {user['user_id']} in session {user['session_id']}")
        print('='*50)
        
        try:
            result = await manager.run_workflow(
                workflow_name="weather_assistant",
                input_text=user["query"],
                user_id=user["user_id"],
                session_id=user["session_id"]
            )
            results.append(result)
        except Exception as e:
            print(f"Error running workflow for {user['user_id']}: {e}")
    
    # Demonstrate session reuse
    print(f"\n{'='*50}")
    print("Reusing session for user_001")
    print('='*50)
    
    try:
        result = await manager.run_workflow(
            workflow_name="weather_assistant",
            input_text="What about the weather in Paris?",
            user_id="user_001",
            session_id="sess_001"  # Reusing the same session
        )
        results.append(result)
    except Exception as e:
        print(f"Error running workflow for user_001: {e}")
    
    print("\nAll workflows completed!")
    return results


if __name__ == "__main__":
    print("🚀 Starting Multi-User Agents Manager Example 🚀")
    asyncio.run(main())
    print("\n✅ Multi-user example completed!")