# Agents Manager Module Documentation

## Overview

The Agents Manager module provides a flexible and dynamic way to create and manage agent workflows using Google's Agent Development Kit (ADK). Instead of hard-coding agent configurations, users can define agents and workflows through configuration objects, making the system highly adaptable and reusable.

The module is designed with multi-user support in mind, allowing proper session management for different users and sessions. It also features a modular UI system that separates the presentation layer from the business logic.

## Key Components

### 1. AgentsManager
The main orchestrator class that manages agent creation, workflow registration, and execution.

### 2. WorkflowBuilder
A builder pattern implementation for creating complex agent workflows with a fluent API.

### 3. AgentFactory
A factory pattern implementation for creating different types of agents based on configuration.

### 4. TerminalUIManager
A dedicated UI manager for handling all terminal output using the rich library, separating UI concerns from business logic.

### 5. Agent Types
Configuration schemas and enums for defining different agent types.

## UI Module

The Agents Manager includes a dedicated UI module (`modules/ui/terminal_ui_manager.py`) that handles all terminal output using the rich library. This separation of concerns allows for:

1. **Cleaner Code**: Business logic is separated from presentation logic
2. **Easier Maintenance**: UI changes can be made without affecting core functionality
3. **Better Testability**: UI components can be tested independently
4. **Flexibility**: Different UI implementations can be swapped in the future

The `TerminalUIManager` class provides methods for all common UI operations such as printing headers, workflow information, session details, errors, and agent responses.

To use the Agents Manager module, ensure you have the required dependencies:

```bash
pip install google-adk rich python-dotenv pydantic
```

## Quick Start

Here's a simple example to get you started:

```python
from modules.core.agents_manager import AgentsManager

# Create the manager with an app name
manager = AgentsManager(app_name="my_app")

# Create a simple agent
manager.create_workflow_builder("simple_agent")\
    .add_llm_agent(
        name="assistant",
        model="gemini-2.0-flash",
        instruction="You are a helpful assistant."
    )\
    .set_entry_point("assistant")\
    .build()

# Run the agent for a specific user and session
result = await manager.run_workflow(
    workflow_name="simple_agent",
    input_text="Hello, how are you?",
    user_id="user_123",
    session_id="session_456"  # Optional, will create new if None
)
```

## Detailed Usage

### Creating Agents

The module supports several types of agents:

#### LLM Agents
Standard language model agents with customizable instructions and tools:

```python
builder.add_llm_agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research the given topic using available tools.",
    tools=["web_search", "database_query"],
    output_key="research_findings"
)
```

#### Sequential Agents
Execute sub-agents in sequence, passing state between them:

```python
builder.add_sequential_agent(
    name="research_and_write",
    sub_agents=["researcher", "writer"],
    description="Research a topic and write a summary"
)
```

#### Parallel Agents
Execute sub-agents concurrently:

```python
builder.add_parallel_agent(
    name="data_collector",
    sub_agents=["stock_researcher", "sentiment_analyst", "risk_assessor"],
    description="Collect financial data in parallel"
)
```

#### Loop Agents
Repeat sub-agents until a condition is met or max iterations reached:

```python
builder.add_loop_agent(
    name="iterative_refiner",
    sub_agents=["writer", "reviewer", "approval_checker"],
    max_iterations=5,
    description="Iteratively refine content until approved"
)
```

### Registering Tools

Tools are functions that agents can call to perform specific actions:

```python
def web_search(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return f"Results for {query}"

# Register the tool
manager.register_tool("web_search", web_search)
```

### Building Workflows

Use the WorkflowBuilder to create complex workflows:

```python
# Create a workflow builder
builder = manager.create_workflow_builder("financial_analysis")

# Add agents to the workflow
builder.add_llm_agent(
    name="analyst",
    model="gemini-2.0-flash",
    instruction="Analyze financial data.",
    tools=["get_stock_price"]
)

# Set entry point and build
workflow = builder.set_entry_point("analyst").build()

# Register the workflow
manager.register_workflow(workflow)
```

### Running Workflows

Execute workflows with input text, specifying user and session:

```python
result = await manager.run_workflow(
    workflow_name="financial_analysis",
    input_text="Analyze Apple's stock performance",
    user_id="user_123",
    session_id="session_456"  # Optional, will create new if None
)

# Access results
final_output = result["final_output"]
session_state = result["session_state"]
session_id = result["session_id"]
user_id = result["user_id"]
events = result["events"]
```

## Multi-User Support

The Agents Manager is designed to support multiple users with proper session management:

1. **App Name**: Identifies your application
2. **User ID**: Identifies individual users
3. **Session ID**: Identifies specific user sessions (optional, auto-generated if not provided)

This allows for:
- Isolated state management per user
- Session continuity across multiple interactions
- Proper resource cleanup and management

## API Reference

### AgentsManager Methods

| Method | Description |
|--------|-------------|
| `AgentsManager(app_name)` | Constructor with app name |
| `register_tool(name, tool_func)` | Register a tool function |
| `register_agent(name, agent)` | Register a pre-created agent |
| `create_workflow_builder(name)` | Create a new workflow builder |
| `register_workflow(workflow_config)` | Register a workflow configuration |
| `get_workflow(name)` | Get a workflow configuration by name |
| `list_workflows()` | List all registered workflow names |
| `run_workflow(name, input_text, user_id, session_id)` | Execute a registered workflow |
| `print_workflow_info(name)` | Print information about a workflow |

### WorkflowBuilder Methods

| Method | Description |
|--------|-------------|
| `set_description(description)` | Set the workflow description |
| `add_llm_agent(...)` | Add an LLM agent to the workflow |
| `add_sequential_agent(...)` | Add a sequential agent |
| `add_parallel_agent(...)` | Add a parallel agent |
| `add_loop_agent(...)` | Add a loop agent |
| `set_entry_point(agent_name)` | Set the workflow entry point |
| `build()` | Build and return the workflow configuration |

## Best Practices

1. **Modular Design**: Create specialized agents for specific tasks rather than monolithic agents.
2. **Clear Instructions**: Write precise, unambiguous instructions for each agent.
3. **Tool Registration**: Register all required tools before creating agents that use them.
4. **Error Handling**: Implement proper error handling for tool failures and agent errors.
5. **State Management**: Use `output_key` to store important results in session state for use by subsequent agents.
6. **Workflow Validation**: Always validate workflows before running them in production.
7. **Session Management**: Use meaningful user_id and session_id values for proper isolation.
8. **Resource Cleanup**: Ensure proper cleanup of resources in long-running applications.

## Examples

See the `src/example_usage.py`, `src/advanced_example.py`, and `src/multi_user_example.py` files for complete working examples.