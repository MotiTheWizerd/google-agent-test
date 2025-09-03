# ADK Google Docs Test

A test project for working with Google's Agent Development Kit (ADK).

## Overview

This project demonstrates how to create a flexible and dynamic agent management system using Google's Agent Development Kit (ADK). The system allows users to define agent workflows through configuration rather than hard-coding, making it highly adaptable and reusable.

The module is designed with multi-user support in mind, allowing proper session management for different users and sessions.

## Documentation

See the [agent_manager_docs](agent_manager_docs/) directory for complete documentation:

- [Agents Manager Overview](agent_manager_docs/agents_manager.md)
- [Usage Examples](agent_manager_docs/usage_examples.md)
- [API Reference](agent_manager_docs/api_reference.md)
- [Memory Module](agent_manager_docs/memory_module.md)

## Examples

- [Basic Example](src/example_usage.py)
- [Advanced Example](src/advanced_example.py)
- [Multi-User Example](src/multi_user_example.py)
- [Streaming Example](src/streaming_example.py)
- [Memory Integration Example](src/memory_integration_example.py)

## Features

- **Dynamic Agent Creation**: Define agents through configuration objects
- **Multiple Agent Types**: Support for LLM, Sequential, Parallel, and Loop agents
- **Workflow Builder**: Intuitive builder pattern for creating complex workflows
- **Tool Registration**: Easy registration and management of tools
- **Session Management**: Built-in session handling with state persistence
- **Multi-User Support**: Proper isolation and management of multiple users
- **Streaming Support**: Real-time event processing for progressive output
- **Rich Logging**: Beautiful console output using the `rich` library
- **Memory Integration**: Seamless integration with external memory systems like Mem0

## Installation

The project uses Poetry for dependency management:

```bash
poetry install
```

The required dependencies are specified in `pyproject.toml` and include `google-adk`, `rich`, `python-dotenv`, `pydantic`, and `mem0ai`.

## Quick Start

```python
from modules.core.agents_manager import AgentsManager

# Create the manager with an app name
manager = AgentsManager(app_name="my_app")

# Create a simple workflow
builder = manager.create_workflow_builder("simple_workflow")
builder.add_llm_agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant."
).set_entry_point("assistant").build()

# Register and run for a specific user
manager.register_workflow(workflow)
result = await manager.run_workflow(
    workflow_name="simple_workflow",
    input_text="Hello, how are you?",
    user_id="user_123",
    session_id="session_456"  # Optional, will create new if None
)

# Or stream for real-time output
async for event in manager.stream_workflow(
    workflow_name="simple_workflow",
    input_text="Hello, how are you?",
    user_id="user_123",
    session_id="session_456"
):
    # Process events as they occur
    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
        for part in event.content.parts:
            if hasattr(part, 'text') and part.text:
                print(part.text, end='', flush=True)
```