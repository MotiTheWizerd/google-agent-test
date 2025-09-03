# Memory Module Documentation

## Overview

The Memory module provides a robust interface for integrating external memory systems with the Agents Manager. It follows a clean architecture pattern with a stable interface that can support multiple memory backends.

## Module Structure

```
src/modules/memory/
├── __init__.py
├── config.py
├── errors.py
├── interfaces.py
├── models.py
├── adapters/
│   └── mem0_store.py
├── utils/
│   └── retry.py
└── tests/
    └── test_mem0_store.py
```

## Key Components

### 1. Interfaces (`interfaces.py`)
Defines the stable interface that all memory implementations must adhere to:
- `MemoryStore`: Protocol defining the contract for memory operations
- `MemoryRecord`: TypedDict for memory record structure
- `SearchResult`: TypedDict for search result structure

### 2. Configuration (`config.py`)
Handles configuration for memory systems:
- `Mem0Config`: Dataclass for Mem0 configuration with environment variable support

### 3. Errors (`errors.py`)
Custom exception hierarchy:
- `Mem0Error`: Base exception
- `Mem0AuthError`: Authentication errors
- `Mem0NotFound`: Resource not found errors
- `Mem0RateLimited`: Rate limiting errors

### 4. Models (`models.py`)
Pydantic models for data validation:
- `MemoryRecordModel`: Model for memory records
- `SearchResultModel`: Model for search results
- `ExportSchemaModel`: Model for export schemas

### 5. Adapters (`adapters/mem0_store.py`)
Concrete implementations of the memory interface:
- `Mem0Store`: Mem0 implementation of MemoryStore

### 6. Utilities (`utils/retry.py`)
Helper functions:
- `with_retry`: Retry function with exponential backoff

## API Updates

### Recent Changes
The Mem0 adapter has been updated to work with the latest Mem0 API:
- Method names updated from `add_memory`/`search_memories` to `add`/`search`
- The `add` method now requires a `messages` parameter in the format `[{"role": "user", "content": text}]`
- Added `output_format="v1.1"` parameter to avoid deprecation warnings
- Improved handling of search results to work with the new response format

## Usage

### Basic Setup

```python
from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config

# Initialize from environment variables
config = Mem0Config.from_env()
store = Mem0Store(config)
```

### Adding Memories

```python
record = store.add(
    user_id="user_123",
    text="I prefer window seats on flights",
    tags=["preference", "travel"],
    metadata={"source": "chat"}
)
```

### Searching Memories

```python
results = store.search(
    user_id="user_123",
    query="seat preference",
    k=5
)
```

### Integration with Agents

The memory module can be integrated with the Agents Manager to provide context-aware responses:

```python
from src.modules.core.agents_manager import AgentsManager
from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config

# Initialize memory store
mem_store = Mem0Store(Mem0Config.from_env())

# Store user preferences
mem_store.add(
    user_id="user_123",
    text="User prefers technical explanations with code examples",
    tags=["preference"]
)

# Recall context when needed
def build_contextual_prompt(user_id: str, task: str) -> str:
    memories = mem_store.search(user_id=user_id, query=task, k=5)
    context = "\n".join([m["record"]["text"] for m in memories])
    return f"Context:\n{context}\n\nTask: {task}"
```

## Best Practices

1. **Boundary Management**: Only store durable, identity-level facts. Use classifiers or rules to avoid dumping raw chat.

2. **PII Handling**: Tag and encrypt (or avoid storing) sensitive fields. Use tags like `["pii:email"]` to control retrieval.

3. **Conflict Resolution**: When new info contradicts old, add a new memory plus a metadata pointer to the previous record.

4. **Latency Considerations**: Do not block the main response on writes; fire-and-forget store, but block on search before LLM calls.

5. **Observability**: Log user_id, memory_id, top-k, scores, and which memories actually influenced a response.

## Testing

The module includes a test suite with mocked clients for unit testing:

```bash
# Run tests with pytest
pytest src/modules/memory/tests/
```

## Environment Variables

The module uses the following environment variables:

- `MEM0_API_KEY`: API key for Mem0 (required)
- `MEM0_ORG_ID`: Organization ID (optional)
- `MEM0_PROJECT_ID`: Project ID (optional)
- `MEM0_TIMEOUT_S`: Timeout in seconds (default: 15.0)
```