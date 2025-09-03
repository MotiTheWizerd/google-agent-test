# ADK Developer Guide — **Context**

> Target: engineers building agents with Google’s Agent Development Kit (ADK). This guide distills how **context** works and how to use it in tools, callbacks, and agents — with copy‑pasteable examples.

---

## Mental model
In ADK, **context** is the bundle of information and services your agent/tool has for the current request–response run (an *invocation*). It powers:

- **State** across steps (session data, per‑user/app flags)
- **Data passing** between tools/callbacks in the same invocation
- **Services** access: artifacts, memory, authentication, session service
- **Identity & tracking**: `agent.name`, `invocation_id`, function call IDs (for tools)

The framework constructs an **`InvocationContext`** at the start of a run and threads the appropriate, more focused context into your code: `ReadonlyContext`, `CallbackContext`, or `ToolContext`.

---

## Context types (cheatsheet)

| Context | Where you get it | Read state | Write state | Artifacts | Memory search | Auth | Function Call ID | End invocation |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `ReadonlyContext` | instruction providers / read‑only hooks | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `CallbackContext` | agent/model callbacks (`before_*`, `after_*`) | ✅ | ✅ | ✅ `save/load_artifact` | ❌ | ❌ | ❌ | ✅ via underlying flag |
| `ToolContext` | function tools & tool callbacks | ✅ | ✅ | ✅ (incl. `list_artifacts`) | ✅ `search_memory` | ✅ `request_credential/get_auth_response` | ✅ `function_call_id` | ✅ via underlying flag |
| `InvocationContext` | agent core (`_run_async_impl`, `_run_live_impl`) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ set `ctx.end_invocation = True` |

> **State prefixes** (when using a persistent SessionService):
> - `app:` — app‑wide value (shared across sessions)
> - `user:` — user‑wide value (shared across this user’s sessions)
> - `temp:` — ephemeral for the current invocation only

---

## Access patterns & examples (Python)

### 1) Read state & identifiers (Tool)
```python
from google.adk.tools import ToolContext

def my_tool(tool_context: ToolContext, **kwargs):
    user_pref = tool_context.state.get("user:ui_theme", "light")
    api_endpoint = tool_context.state.get("app:api_endpoint")

    agent = tool_context.agent_name
    inv_id = tool_context.invocation_id
    func_id = getattr(tool_context, "function_call_id", "N/A")

    print(f"[{inv_id}] {agent} func={func_id} using {api_endpoint} (theme={user_pref})")
    # ...do work...
    return {"ok": True}
```

### 2) Pass data between tools in one run
```python
# Tool 1 — produce data
from google.adk.tools import ToolContext
import uuid

def get_user_profile(tool_context: ToolContext) -> dict:
    user_id = str(uuid.uuid4())  # simulate lookup
    tool_context.state["temp:current_user_id"] = user_id  # ephemeral for this invocation
    return {"profile_status": "ID generated"}

# Tool 2 — consume data
from google.adk.tools import ToolContext

def fetch_orders(tool_context: ToolContext) -> dict:
    user_id = tool_context.state.get("temp:current_user_id")
    if not user_id:
        return {"error": "no user_id in state"}
    # ...fetch orders for user_id...
    return {"orders": ["#A102", "#A103"]}
```

> **How persistence works:** changes you make via `context.state[...] = ...` are recorded into the current step’s `EventActions.state_delta` and applied by the `SessionService`.

### 3) Work with artifacts (files, URIs)
```python
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# Save a reference (path/URI) as an artifact

def save_document_reference(context: CallbackContext, file_path: str) -> None:
    part = types.Part(text=file_path)  # store the reference, not the whole file
    version = context.save_artifact("document_to_summarize.txt", part)
    context.state["temp:last_saved_artifact_version"] = version

# Later: load it

def load_document_reference(context: CallbackContext) -> str:
    part = context.load_artifact("document_to_summarize.txt")
    return getattr(part, "text", None)

# In tools you can also list
from google.adk.tools import ToolContext

def list_all(tool_context: ToolContext):
    files = tool_context.list_artifacts()
    return {"artifacts": files}
```

### 4) Authentication inside tools
```python
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig  # configure for API key / OAuth etc.

MY_AUTH = AuthConfig(...)
AUTH_STATE_KEY = "user:thirdparty_api_credential"

def call_secure_api(tool_context: ToolContext, payload: dict) -> dict:
    cred = tool_context.state.get(AUTH_STATE_KEY)
    if not cred:
        # This *pauses* the tool: the framework will yield an event asking for auth
        tool_context.request_credential(MY_AUTH)
        return {"status": "auth_required"}

    # proceed with the secure call using `cred`
    # ... do request ...
    return {"result": "ok"}
```
> On a subsequent turn, the framework links the provided credential back to this tool call via `function_call_id`, and `state[AUTH_STATE_KEY]` (or `get_auth_response`) will be set.

### 5) Leverage memory from a tool
```python
from google.adk.tools import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    result = tool_context.search_memory(f"Information about {topic}")
    if result and getattr(result, "results", None):
        top = result.results[0]
        return {"snippet": top.text}
    return {"message": "no relevant memories"}
```

### 6) Access initial user input (Callback)
```python
from google.adk.agents.callback_context import CallbackContext

def check_initial_intent(cb: CallbackContext):
    text = ""
    if cb.user_content and cb.user_content.parts:
        text = cb.user_content.parts[0].text or "<non-text>"
    print("Invocation started with:", text)
```

### 7) Advanced: control flow in the agent core
```python
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if not ctx.memory_service:
            print("Memory not available — changing behavior")
        if ctx.session.state.get("critical_error_flag"):
            ctx.end_invocation = True
            yield Event(author=self.name, invocation_id=ctx.invocation_id,
                        content="Stopping due to critical error.")
            return
        # ... normal flow ...
        yield Event(author=self.name, invocation_id=ctx.invocation_id,
                    content="Work complete.")
```

---

## Best practices
- **Use the most specific context** you’re given (`ToolContext` in tools, `CallbackContext` in callbacks). Only touch `InvocationContext` in agent cores.
- **Prefer `state` for data flow**, not globals. Use prefixes (`app:`, `user:`, `temp:`) intentionally.
- **Store references in artifacts**, not large blobs in state. Load on demand.
- **Authentication is a two‑step dance.** `request_credential()` yields; resume next turn and read the stored credential.
- **Always log IDs** (`invocation_id`, `agent_name`, `function_call_id`) for observability.
- **Keep tools pure**: accept primitives, return JSON‑serializable outputs; read side‑inputs from `tool_context` only.

---

## Troubleshooting quick hits
- *My tool can’t see data from a previous tool*: ensure you wrote to `state[...]` (not a local variable) and used the same invocation; for cross‑invocation, use `user:`/`app:` prefixes with a persistent `SessionService`.
- *Auth keeps getting requested again*: check you’re storing credentials under a durable key (e.g., `user:...`) rather than `temp:`.
- *Artifact content vs reference confusion*: store a **reference** as a text `Part`; retrieve and dereference as needed.
- *Callbacks not mutating state*: only `CallbackContext`/`ToolContext` are writable; `ReadonlyContext` isn’t.

---

## Minimal Java parallels (sketch)
```java
import com.google.adk.tools.ToolContext;

public Map<String, Object> searchExternalApi(String q, ToolContext ctx){
  String apiKey = ctx.state().get("user:api_key");
  if(apiKey == null){
    // ctx.requestCredential(authConfig);
    return Map.of("status", "auth_required");
  }
  return Map.of("result", "ok");
}
```

---

## Reference
- ADK **Context** concepts, APIs, and patterns as presented in Google’s ADK documentation.

