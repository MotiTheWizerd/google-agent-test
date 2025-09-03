# Agents Manager Documentation

Welcome to the documentation for the Agents Manager module, a flexible and dynamic agent management system built on top of Google's Agent Development Kit (ADK).

## Table of Contents

1. [Agents Manager Overview](agents_manager.md) - Complete documentation of the module
2. [Usage Examples](usage_examples.md) - Practical examples and use cases
3. [API Reference](api_reference.md) - Detailed API documentation

## Getting Started

The Agents Manager module allows you to create agent workflows dynamically through configuration rather than hard-coding. This makes it easy to build flexible, reusable agent systems.

### Key Features

- **Dynamic Agent Creation**: Define agents through configuration objects
- **Multiple Agent Types**: Support for LLM, Sequential, Parallel, and Loop agents
- **Workflow Builder**: Intuitive builder pattern for creating complex workflows
- **Tool Registration**: Easy registration and management of tools
- **Session Management**: Built-in session handling with state persistence
- **Rich Logging**: Beautiful console output using the `rich` library

### Installation

Make sure you have the required dependencies installed:

```bash
pip install google-adk rich python-dotenv pydantic
```

### Quick Example

```python
from modules.core.agents_manager import AgentsManager

# Create manager
manager = AgentsManager()

# Create a simple workflow
builder = manager.create_workflow_builder("simple_workflow")
builder.add_llm_agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant."
).set_entry_point("assistant").build()

# Register and run
manager.register_workflow(workflow)
result = await manager.run_workflow("simple_workflow", "Hello, how are you?")
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

docs/
├── agents_manager.md          # Complete documentation
├── usage_examples.md         # Practical examples
└── api_reference.md          # API reference (coming soon)

examples/
├── example_usage.py          # Basic example
└── advanced_example.py       # Advanced example
```

## Next Steps

1. Read the [Agents Manager Overview](agents_manager.md) for complete documentation
2. Check out the [Usage Examples](usage_examples.md) for practical implementations
3. Run the example scripts in the `src` directory
4. Experiment with creating your own workflows

## Support

For issues, questions, or contributions, please open an issue on the project repository.