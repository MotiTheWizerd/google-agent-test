# Agents Manager Documentation

Welcome to the documentation for the Agents Manager module, a flexible and dynamic agent management system built on top of Google's Agent Development Kit (ADK).

## Table of Contents

1. [Agents Manager Overview](agents_manager.md) - Complete documentation of the module
2. [Usage Examples](usage_examples.md) - Practical examples and use cases
3. [API Reference](api_reference.md) - Detailed API documentation
4. [Memory Module](memory_module.md) - Documentation for the memory integration module
5. [Web Scraper Module](web_scraper_module.md) - Documentation for the web scraping tools

## Getting Started

The Agents Manager module allows you to create agent workflows dynamically through configuration rather than hard-coding. This makes it easy to build flexible, reusable agent systems.

### Key Features

- **Dynamic Agent Creation**: Define agents through configuration objects
- **Multiple Agent Types**: Support for LLM, Sequential, Parallel, and Loop agents
- **Workflow Builder**: Intuitive builder pattern for creating complex workflows
- **Tool Registration**: Easy registration and management of tools
- **Session Management**: Built-in session handling with state persistence
- **Rich Logging**: Beautiful console output using the `rich` library
- **Modular Architecture**: Refactored into smaller, more focused modules
- **Memory Integration**: Seamless integration with external memory systems like Mem0
- **Web Scraping Tools**: Integration with Firecrawl for web scraping, crawling, and extraction

### Installation

Make sure you have the required dependencies installed. The project uses Poetry for dependency management:

```bash
poetry install
```

The required dependencies are specified in `pyproject.toml` and include `google-adk`, `rich`, `python-dotenv`, `pydantic`, `mem0ai`, and `firecrawl-py`.

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
    ├── core/
    │   └── agents_manager/
    │       ├── __init__.py               # Package initialization
    │       ├── agents_manager.py         # Main orchestrator
    │       ├── workflow_manager.py       # Workflow registration and management
    │       ├── session_manager.py        # Session creation and management
    │       ├── runner_manager.py         # Runner creation and management
    │       ├── workflow_executor.py      # Workflow execution orchestration
    │       ├── agent_factory.py          # Factory for creating agents
    │       ├── workflow_builder.py       # Builder for workflows
    │       ├── agent_types.py            # Configuration schemas
    │       └── ... (test files)
    ├── memory/                          # Memory integration module
    │   ├── __init__.py                  # Package initialization
    │   ├── config.py                    # Configuration management
    │   ├── errors.py                    # Custom exceptions
    │   ├── interfaces.py                # Stable interfaces
    │   ├── models.py                    # Data models
    │   ├── adapters/                    # Memory system adapters
    │   │   └── mem0_store.py            # Mem0 implementation
    │   ├── utils/                       # Utility functions
    │   │   └── retry.py                 # Retry utilities
    │   └── tests/                       # Test suite
    │       └── test_mem0_store.py       # Tests for Mem0 adapter
    └── tools/                           # Tool modules
        └── web_scraper/                 # Web scraping tools
            ├── __init__.py              # Package initialization
            ├── client.py                # Firecrawl client implementation
            ├── firecrawl_tools.py       # Agent-oriented tool functions
            └── types.py                 # Data classes for options

docs/
├── agents_manager.md          # Complete documentation
├── usage_examples.md         # Practical examples
├── memory_module.md          # Memory module documentation
├── web_scraper_module.md     # Web scraper module documentation
└── api_reference.md          # API reference

examples/
├── example_usage.py          # Basic example
└── advanced_example.py       # Advanced example
```

## Next Steps

1. Read the [Agents Manager Overview](agents_manager.md) for complete documentation
2. Check out the [Usage Examples](usage_examples.md) for practical implementations
3. Read the [Memory Module](memory_module.md) documentation for memory integration
4. Read the [Web Scraper Module](web_scraper_module.md) documentation for web scraping tools
5. Run the example scripts in the `src` directory
6. Experiment with creating your own workflows

## Support

For issues, questions, or contributions, please open an issue on the project repository.