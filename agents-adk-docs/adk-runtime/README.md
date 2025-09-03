# ADK Runtime Starter — *Running Agents*

A tiny, working project that shows **how to run ADK agents** using the **Runtime** (event loop + Runner)
with **streaming vs non‑streaming**, **state updates**, and **RunConfig**.

> Install: `pip install google-adk`

## What’s inside
- `docs/` — concise developer docs (Runtime overview, RunConfig, events/streaming, sessions/state).
- `src/agents/root_agent.py` — minimal LLM agent with a tool.
- `src/tools/hello_tool.py` — tiny function tool.
- `src/run_local_async.py` — run with `Runner.run_async(...)` and stream events.
- `src/run_local_sync.py` — run with `Runner.run(...)` (convenience).
- `src/run_with_vertex_sessions.py` — skeleton showing `VertexAiSessionService`.
- `requirements.txt` — minimal Python deps.

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Async streaming run
python src/run_local_async.py "hi, can you greet me and say today's date?"

# Sync run (no manual async)
python src/run_local_sync.py "short summary of ADK runtime"
```
