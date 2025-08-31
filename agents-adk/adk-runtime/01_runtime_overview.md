# Runtime Overview (ADK)

The **ADK Runtime** is the engine that orchestrates your agents, tools, and callbacks via an **event loop**.
- The **Runner** kicks off an invocation, calls your agent’s `run_async`, and **processes each yielded `Event`**.
- Your agent/tool/callback logic **yields events** whenever there’s output or a state/artifact change; the Runner commits changes through services and then allows logic to resume. citeturn1view0

## Core Roles
- **Runner (orchestrator)** — receives user input, appends it to the session, starts the agent, processes each yielded event (committing state/artifact deltas), and forwards events upstream (e.g., UI). citeturn1view0
- **Execution Logic** — your `Agent` (often an `LlmAgent`), `Tools`, and `Callbacks`. They compute, then **yield** `Event`s back to the Runner. citeturn1view0
- **InvocationContext & Session** — ADK creates an invocation context when `runner.run_async(...)` starts; session tracks history/state. citeturn4search8

## Important Behaviors
- **State commits happen on yield**: changes you put into the event’s `state_delta` are **guaranteed** after the Runner processes that event and logic **resumes**. Plan reads accordingly. citeturn1view0
- **Streaming vs Non‑Streaming**: with streaming, you’ll see partial events until a final event (`partial=False` / `event.is_final_response()`). Non‑streaming emits a single final event. citeturn1view0
- **Async is primary**: `Runner.run_async` is the main entry point; there’s also a sync convenience `Runner.run`. citeturn1view0turn5view0

## API Surface you’ll use most
- `Runner.run_async(user_id, session_id, new_message)` → async event stream.
- `Runner.run(...)` → sync wrapper.
- `Event` helpers like `event.is_final_response()`. citeturn5view0turn6view0
