# Usage Guide: Agents Manager Module

This guide provides practical examples of how to use the Agents Manager module to create dynamic agent workflows with proper multi-user support.

## Example 1: Simple Research Assistant

This example demonstrates a basic research workflow with a single agent.

```python
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

# Mock tool for web search
def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': This is a mock search result."

async def simple_research_example():
    """Simple research assistant example."""
    # Create agents manager with app name
    manager = AgentsManager(app_name="simple_research_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create workflow using builder
    builder = manager.create_workflow_builder("research_assistant")
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="You are a research assistant. Use the web_search tool to find information about topics. Provide concise, accurate answers.",
        tools=["web_search"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("researcher").build()
    manager.register_workflow(workflow)
    
    # Run the workflow for a specific user
    result = await manager.run_workflow(
        workflow_name="research_assistant", 
        input_text="What are the latest developments in quantum computing?",
        user_id="researcher_001",
        session_id="session_001"
    )
    
    return result

# Run the example
if __name__ == "__main__":
    print("Running Simple Research Assistant Example...")
    result = asyncio.run(simple_research_example())
    print("Example completed!")
```

## Example 2: Streaming Research Assistant

This example demonstrates how to use the streaming functionality to get real-time responses.

```python
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

# Mock tool for web search
def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': This is a mock search result."

async def streaming_research_example():
    """Streaming research assistant example."""
    # Create agents manager with app name
    manager = AgentsManager(app_name="streaming_research_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create workflow using builder
    builder = manager.create_workflow_builder("streaming_research_assistant")
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="You are a research assistant. Use the web_search tool to find information about topics. Provide detailed, comprehensive answers with step-by-step explanations.",
        tools=["web_search"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("researcher").build()
    manager.register_workflow(workflow)
    
    # Stream the workflow for a specific user
    print("Streaming response:")
    full_response = ""
    
    async for event in manager.stream_workflow(
        workflow_name="streaming_research_assistant",
        input_text="Explain the process of photosynthesis in detail, including the chemical reactions involved.",
        user_id="researcher_001",
        session_id="stream_session_001"
    ):
        # Process different types of events
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    # Print streaming text as it arrives
                    print(part.text, end='', flush=True)
                    full_response += part.text
        
        # Handle final response
        if event.is_final_response():
            print("

[Final response received]")
    
    print(f"

Full response collected: {len(full_response)} characters")
    return full_response

# Run the example
if __name__ == "__main__":
    print("Running Streaming Research Assistant Example...")
    result = asyncio.run(streaming_research_example())
    print("Example completed!")
```

## Example 3: Multi-User Weather Assistant

This example demonstrates multi-user support with session management.

```python
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

# Mock tool for weather
def get_weather(location: str) -> str:
    """Mock weather tool."""
    return f"The weather in {location} is sunny with a temperature of 22°C."

async def multi_user_weather_example():
    """Multi-user weather assistant example."""
    # Create agents manager
    manager = AgentsManager(app_name="weather_app")
    
    # Register tools
    manager.register_tool("get_weather", get_weather)
    
    # Create weather agent
    builder = manager.create_workflow_builder("weather_assistant")
    builder.add_llm_agent(
        name="weather_agent",
        model="gemini-2.0-flash",
        instruction="You are a weather assistant. Use the get_weather tool to provide weather information.",
        tools=["get_weather"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("weather_agent").build()
    manager.register_workflow(workflow)
    
    # Simulate multiple users
    users = [
        {"user_id": "user_001", "session_id": "sess_001", "location": "New York"},
        {"user_id": "user_002", "session_id": "sess_002", "location": "London"},
        {"user_id": "user_003", "session_id": "sess_003", "location": "Tokyo"},
    ]
    
    # Run workflows for each user
    results = []
    for user in users:
        result = await manager.run_workflow(
            workflow_name="weather_assistant",
            input_text=f"What's the weather like in {user['location']}?",
            user_id=user["user_id"],
            session_id=user["session_id"]
        )
        results.append(result)
    
    return results

# Run the example
if __name__ == "__main__":
    print("Running Multi-User Weather Assistant Example...")
    results = asyncio.run(multi_user_weather_example())
    print("Example completed!")
```

## Example 4: Session Continuity

This example shows how to reuse sessions for continuous conversations.

```python
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

# Mock tools
def get_weather(location: str) -> str:
    """Mock weather tool."""
    return f"The weather in {location} is sunny with a temperature of 22°C."

def get_forecast(location: str, days: int = 3) -> str:
    """Mock forecast tool."""
    return f"{days}-day forecast for {location}: Sunny with highs around 22°C."

async def session_continuity_example():
    """Session continuity example."""
    # Create agents manager
    manager = AgentsManager(app_name="continuity_app")
    
    # Register tools
    manager.register_tool("get_weather", get_weather)
    manager.register_tool("get_forecast", get_forecast)
    
    # Create weather assistant
    builder = manager.create_workflow_builder("weather_assistant")
    builder.add_llm_agent(
        name="weather_agent",
        model="gemini-2.0-flash",
        instruction="You are a weather assistant. Use the get_weather and get_forecast tools to provide weather information.",
        tools=["get_weather", "get_forecast"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("weather_agent").build()
    manager.register_workflow(workflow)
    
    # User interaction 1 - Create new session
    result1 = await manager.run_workflow(
        workflow_name="weather_assistant",
        input_text="What's the weather like in Paris?",
        user_id="traveler_001",
        session_id="travel_session_001"
    )
    
    # User interaction 2 - Reuse session for continuity
    result2 = await manager.run_workflow(
        workflow_name="weather_assistant",
        input_text="What about the 5-day forecast?",
        user_id="traveler_001",
        session_id="travel_session_001"  # Same session for continuity
    )
    
    return [result1, result2]

# Run the example
if __name__ == "__main__":
    print("Running Session Continuity Example...")
    results = asyncio.run(session_continuity_example())
    print("Example completed!")
```

## Example 5: Complex Multi-Agent Workflow

This example shows a complex workflow with multiple agent types.

```python
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

# Mock tools
def search_web(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': Relevant information found."

def get_stock_price(symbol: str) -> str:
    """Mock stock price tool."""
    prices = {"AAPL": "$192.55", "GOOGL": "$165.73", "MSFT": "$342.53"}
    return f"Current price of {symbol}: {prices.get(symbol, 'Unknown')}"

async def complex_workflow_example():
    """Complex multi-agent workflow example."""
    # Create agents manager
    manager = AgentsManager(app_name="complex_analysis_app")
    
    # Register tools
    manager.register_tool("search_web", search_web)
    manager.register_tool("get_stock_price", get_stock_price)
    
    # Create research agent
    builder = manager.create_workflow_builder("market_analyzer")
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="Research technology companies using search_web tool.",
        tools=["search_web"],
        output_key="research_data"
    )
    
    # Create stock analyzer
    builder.add_llm_agent(
        name="stock_analyst",
        model="gemini-2.0-flash",
        instruction="Analyze stock prices using get_stock_price tool.",
        tools=["get_stock_price"],
        output_key="stock_analysis"
    )
    
    # Create summary agent
    builder.add_llm_agent(
        name="report_writer",
        model="gemini-2.0-flash",
        instruction="Write a comprehensive market analysis report based on research data and stock analysis."
    )
    
    # Create parallel agent to gather data
    builder.add_parallel_agent(
        name="data_collector",
        sub_agents=["researcher", "stock_analyst"]
    )
    
    # Create sequential workflow
    builder.add_sequential_agent(
        name="analysis_pipeline",
        sub_agents=["data_collector", "report_writer"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("analysis_pipeline").build()
    manager.register_workflow(workflow)
    
    # Run the workflow
    result = await manager.run_workflow(
        workflow_name="market_analyzer",
        input_text="Analyze the technology sector with focus on Apple, Google, and Microsoft",
        user_id="analyst_001",
        session_id="analysis_session_001"
    )
    
    return result

# Run the example
if __name__ == "__main__":
    print("Running Complex Workflow Example...")
    result = asyncio.run(complex_workflow_example())
    print("Example completed!")
```

## Running the Examples

To run these examples:

1. Make sure you have set up your environment with the required API keys
2. Install the dependencies using Poetry: `poetry install`
3. Run any of the examples: `python src/multi_user_example.py`

## Customization

You can customize these examples by:

1. **Changing Models**: Replace `"gemini-2.0-flash"` with other supported models
2. **Adding Tools**: Register your own tools with `manager.register_tool()`
3. **Modifying Instructions**: Adjust agent instructions for different behaviors
4. **Changing Workflows**: Experiment with different agent combinations and workflows
5. **Adding Error Handling**: Implement try/except blocks for production use

## Multi-User Best Practices

1. **Unique User IDs**: Use meaningful, unique identifiers for each user
2. **Session Management**: Reuse session IDs for continuous conversations
3. **Resource Isolation**: Each user/session gets isolated state and resources
4. **Scalability**: The system can handle multiple concurrent users
5. **State Persistence**: Session state is maintained across interactions

## Streaming Best Practices

1. **Real-time Processing**: Use streaming for applications that need real-time responses
2. **Partial Text Handling**: Process partial text chunks as they arrive for immediate display
3. **Event Filtering**: Filter events based on type (text, tool calls, final response) for different handling
4. **Memory Management**: Be mindful of memory usage when collecting full responses
5. **UI Updates**: Update UI progressively as streaming events arrive

## Troubleshooting

Common issues and solutions:

1. **API Key Errors**: Ensure your `.env` file contains valid API keys
2. **Import Errors**: Make sure the `src` directory is in your Python path
3. **Tool Registration**: Ensure all tools used by agents are registered before creating workflows
4. **Workflow Validation**: Check that entry points match existing agent names
5. **Async Issues**: Remember to use `asyncio.run()` when calling async functions
6. **Session Issues**: Verify that user_id and session_id are correctly specified
7. **Streaming Issues**: Ensure you're properly iterating over the async generator for streaming