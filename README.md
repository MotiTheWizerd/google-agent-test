# ADK Google Docs Test

A test project for working with Google's Agent Development Kit (ADK).

## Overview

This project demonstrates how to create a flexible and dynamic agent management system using Google's Agent Development Kit (ADK). The system allows users to define agent workflows through configuration rather than hard-coding, making it highly adaptable and reusable.

The module is designed with multi-user support in mind, allowing proper session management for different users and sessions.

## Documentation

See the [docs](docs/) directory for complete documentation:

- [Agents Manager Overview](docs/agents_manager.md)
- [Usage Examples](docs/usage_examples.md)
- [API Reference](docs/api_reference.md)

## Examples

- [Basic Example](src/example_usage.py)
- [Advanced Example](src/advanced_example.py)
- [Multi-User Example](src/multi_user_example.py)

## Features

- **Dynamic Agent Creation**: Define agents through configuration objects
- **Multiple Agent Types**: Support for LLM, Sequential, Parallel, and Loop agents
- **Workflow Builder**: Intuitive builder pattern for creating complex workflows
- **Tool Registration**: Easy registration and management of tools
- **Session Management**: Built-in session handling with state persistence
- **Multi-User Support**: Proper isolation and management of multiple users
- **Rich Logging**: Beautiful console output using the `rich` library

## Installation

```bash
pip install google-adk rich python-dotenv pydantic
```

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
```