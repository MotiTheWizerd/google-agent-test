# Agents Manager Module

A flexible and dynamic agent management system built on top of Google's Agent Development Kit (ADK). This module allows users to create agent workflows dynamically through configuration rather than hard-coding.

## Features

- **Dynamic Agent Creation**: Define agents through configuration objects
- **Multiple Agent Types**: Support for LLM, Sequential, Parallel, and Loop agents
- **Workflow Builder**: Intuitive builder pattern for creating complex workflows
- **Tool Registration**: Easy registration and management of tools
- **Session Management**: Built-in session handling with state persistence
- **Rich Logging**: Beautiful console output using the `rich` library

## Installation

Make sure you have the required dependencies installed:

```bash
pip install google-adk python-dotenv pydantic rich
```

## Usage

### Basic Example

```python
from modules.core.agents_manager import AgentsManager
from modules.core.workflow_builder import WorkflowBuilder

# Create manager
manager = AgentsManager()

# Register tools
manager.register_tool("search_web", search_web_function)

# Create workflow
builder = manager.create_workflow_builder("research_workflow")
builder.add_llm_agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research the given topic",
    tools=["search_web"]
)
workflow = builder.set_entry_point("researcher").build()

# Register and run
manager.register_workflow(workflow)
result = await manager.run_workflow("research_workflow", "Quantum computing")
```

## Module Structure

```
src/
└── modules/
    └── core/
        ├── agents_manager.py     # Main orchestrator
        ├── agent_factory.py      # Factory for creating agents
        ├── workflow_builder.py   # Builder for workflows
        ├── agent_types.py        # Configuration schemas
        └── __init__.py
```

## Agent Types

1. **LLM Agents**: Standard language model agents with customizable instructions and tools
2. **Sequential Agents**: Execute sub-agents in sequence, passing state between them
3. **Parallel Agents**: Execute sub-agents concurrently
4. **Loop Agents**: Repeat sub-agents until a condition is met or max iterations reached

## API Reference

### AgentsManager

Main class for managing agents and workflows.

- `register_tool(name, tool_func)`: Register a tool function
- `create_workflow_builder(name)`: Create a new workflow builder
- `register_workflow(workflow_config)`: Register a workflow configuration
- `run_workflow(name, input_text)`: Execute a registered workflow

### WorkflowBuilder

Builder class for creating workflows.

- `add_llm_agent(...)`: Add an LLM agent to the workflow
- `add_sequential_agent(...)`: Add a sequential agent
- `add_parallel_agent(...)`: Add a parallel agent
- `add_loop_agent(...)`: Add a loop agent
- `set_entry_point(name)`: Set the workflow entry point
- `build()`: Build and return the workflow configuration

## Examples

See `src/example_usage.py` and `src/advanced_example.py` for complete examples.