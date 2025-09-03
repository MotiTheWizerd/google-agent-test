# ADK Runners — Developer Guide (Python & Java)

This guide explains how to **run agents with ADK Runners** in Python and Java, how events flow, which services are required, and how to stream results in production. It’s written for building UI backends or headless workers that orchestrate ADK agents.

---
## 1) What’s a Runner?
A **Runner** executes an agent inside a session and yields a stream of **Event** objects. It wires your agent to persistence (sessions, memory, artifacts), plugins, and runtime config. In Python there’s a convenient **`InMemoryRunner`** for local/dev; in production you instantiate **`Runner`** and pass real services.

**Why Runners matter**
- Single entrypoint to run an agent for a (user_id, session_id)
- Unified **event stream** (text chunks, tool calls/responses, state/artifact deltas, control signals)
- Pluggable services + global plugins
- Both **standard** and **live (bi‑di)** execution

---
## 2) Lifecycle (mental model)
- **Invocation**: one end‑user message through to the final response
- **Agent call**: one run of a particular agent inside that invocation
- **Step**: a single LLM call (and optional tools) within the agent call
- Runner yields a sequence of **Event**s that encode text, tool calls, results, and state/artifact updates

---
## 3) Python — Core APIs

### 3.1 Classes
- **`InMemoryRunner(agent, app_name='InMemoryRunner', plugins=None)`** — quick local/dev runner with in‑memory services
- **`Runner(app_name, agent, *, session_service, artifact_service=None, memory_service=None, credential_service=None, plugins=None)`** — production form you compose with real services

### 3.2 Methods (high‑level)
- **`run_async(user_id, session_id, new_message, *, state_delta=None, run_config=...) -> AsyncGenerator[Event]`** — **preferred** for production; async event stream
- **`run(user_id, session_id, new_message, *, run_config=...) -> Generator[Event]`** — sync helper for local testing
- **`run_live(user_id, session_id, live_request_queue, *, run_config=...) -> AsyncGenerator[Event]`** — experimental **live** (audio/video/controls) mode

> Tip: prefer `run_async()`; use `run()` only for local demos.

### 3.3 Required Services
At minimum, pass a **`session_service`**. Optionally add **artifact**, **memory**, **credential** services. The in‑memory runner provides dev defaults.

---
## 4) Java — Core APIs
- `Runner(BaseAgent agent, String appName, BaseArtifactService artifactService, BaseSessionService sessionService)`
- `runAsync(userId, sessionId, Content newMessage, RunConfig)` → `Flowable<Event>`
- `runWithSessionId(sessionId, Content newMessage, RunConfig)` → `Flowable<Event>`
- `runLive(…)` for bi‑di/live use‑cases
- `InMemoryRunner` exists for local/dev

---
## 5) Events (what the Runner yields)
Events unify everything the agent and the framework do:
- **Text** (streaming and final)
- **Function calls** (tool invocations requested by the LLM)
- **Function responses** (tool results)
- **State/Artifact** deltas
- **Control signals**: `transfer_to_agent`, `escalate`, `skip_summarization`, etc.

**Final output detection**: use **`event.is_final_response()`** (Python) / `event.finalResponse()` (Java) to decide what’s safe to display as the completed turn.

---
## 6) Plugins (global callbacks)
Attach **plugins** to a Runner to intercept model/tool/agent/run callbacks for logging, metrics, caching, policy, etc.

```python
from typing import Any
from google.adk.plugins import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

class ToolLoggerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="tool_logger")

    async def before_tool_callback(self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext):
        print(f"[tool_logger] calling {tool.name} args={tool_args}")

    async def after_tool_callback(self, *, tool: BaseTool, tool_args: dict, tool_context: ToolContext, result: dict):
        print(f"[tool_logger] result from {tool.name}: {result}")
```

Use: `Runner(..., plugins=[ToolLoggerPlugin(), …])`

---
## 7) RunConfig (tuning execution)
Common fields you’ll control:
- `streaming_mode` — `NONE` or streaming
- `max_llm_calls` — safety guard for tool/looping flows
- `response_modalities`, `input_audio_transcription`, `output_audio_transcription`
- `session_resumption`, `proactivity`, etc.


---
## 8) Python — Minimal Examples

### 8.1 Hello Runner (In‑memory, streaming)
```python
import asyncio
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

agent = LlmAgent(
    name="Greeter",
    description="Greets and answers simply",
    # Configure your model via env/config, or pass model="gemini-1.5-pro" etc.
)

async def main():
    runner = InMemoryRunner(agent)
    user_id = "u-123"
    session_id = "s-1"

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content.make_text("say hello in one sentence")
    ):
        # Streaming text chunks
        if event.content and event.content.parts and getattr(event.content.parts[0], "text", None):
            chunk = event.content.parts[0].text
            if event.partial:
                print(chunk, end="", flush=True)
            else:
                print(chunk)

        # Final response gate for UI
        if hasattr(event, "is_final_response") and event.is_final_response():
            print("\n[final] turn complete")

asyncio.run(main())
```

### 8.2 With a tool + persistent sessions (SQLite)
```python
import asyncio
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.function_tool import function_tool

@function_tool
def add(a: int, b: int) -> dict:
    """Add two integers."""
    return {"sum": a + b}

agent = LlmAgent(name="Calc", tools=[add])
session_service = DatabaseSessionService(db_url="sqlite:///adk.db")

async def main():
    runner = Runner(
        app_name="CalcApp",
        agent=agent,
        session_service=session_service,
    )

    async for event in runner.run_async(
        user_id="u-42",
        session_id="s-42",
        new_message=types.Content.make_text("use add(7, 5) and explain the result")
    ):
        if calls := getattr(event, "get_function_calls", lambda: [])():
            # Framework will execute tools automatically when attached;
            # this branch is useful for logging or custom dispatching.
            for call in calls:
                print("tool call:", call.name, call.args)

        if responses := getattr(event, "get_function_responses", lambda: [])():
            print("tool result:", responses[0].response)

        if hasattr(event, "is_final_response") and event.is_final_response():
            # Use this to display final text to the user
            pass

asyncio.run(main())
```

### 8.3 Adding plugins to a Runner
```python
from google.adk.runners import Runner

runner = Runner(
    app_name="ProdApp",
    agent=agent,
    session_service=session_service,
    plugins=[ToolLoggerPlugin()],
)
```

### 8.4 Live (bi‑di) mode — skeleton
```python
import asyncio
from asyncio import Queue
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import LlmAgent

live_q: Queue = Queue()
# Put microphone chunks / UI controls into live_q

async def main():
    runner = Runner(
        app_name="LiveApp",
        agent=LlmAgent(name="Companion"),
        session_service=DatabaseSessionService(db_url="sqlite:///live.db"),
    )

    async for event in runner.run_live(
        user_id="live-user",
        session_id="live-session",
        live_request_queue=live_q,
    ):
        # Handle streaming audio/text/tool events
        ...

asyncio.run(main())
```

---
## 9) Java — Minimal Example
```java
import com.google.adk.runner.Runner;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.events.Event;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;

// Assume you built a BaseAgent agent = ...
Runner runner = new InMemoryRunner(agent, "DemoApp");

Flowable<Event> stream = runner.runAsync(
    "user-1",
    "session-1",
    Content.builder().addText("hello").build()
);

stream.blockingForEach(event -> {
    event.content().ifPresent(content ->
        content.parts().ifPresent(parts -> {
            if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                System.out.print(parts.get(0).text().get());
            }
        })
    );
    if (event.finalResponse()) {
        System.out.println("\n[final] turn complete");
    }
});
```

---
## 10) Best Practices
- **Use `run_async()`** in Python and subscribe to the stream; avoid blocking UIs
- **Guard loops** with `max_llm_calls` in `RunConfig`
- Use **`event.is_final_response()`** (Python) / `finalResponse()` (Java) instead of ad‑hoc checks
- Prefer **DatabaseSessionService** in prod; keep **InMemoryRunner** for dev
- Keep **plugins** small & composable; log at plugin + agent levels
- Treat **events** as the single source of truth; persist and replay when debugging

---
## 11) Troubleshooting
- **No output?** Verify you’re iterating the stream; in Python an `async for` is required
- **Tools not firing?** Ensure tools are attached to the agent and the model can call tools; check plugin/agent callbacks for short‑circuiting
- **State not saved?** Confirm your `SessionService.append_event` persists deltas; use DB service in prod
- **Live mode oddities?** Consider it experimental; pin ADK versions and test queue back‑pressure

---
## 12) Quick Checklist
- [ ] Choose runner: `InMemoryRunner` (dev) vs `Runner` + services (prod)
- [ ] Wire **SessionService** (DB in prod)
- [ ] (Optional) Memory/Artifact/Credential services
- [ ] Add **plugins** for logging/metrics/policy
- [ ] Stream **events**; detect **final** correctly
- [ ] Set **RunConfig**: streaming + guards

