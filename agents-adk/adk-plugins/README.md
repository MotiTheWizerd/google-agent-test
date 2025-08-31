# ADK Plugins — Developer Guide + Examples

**Target**: Google Agent Development Kit (ADK) — Plugins  
**Goal**: Give your agent a global, reusable way to observe, modify, or short‑circuit execution across agents, tools, and model calls.

> ⚠️ **Note**: The ADK web interface currently **does not support Plugins**. Run via CLI / Python script.

---

## What is a Plugin?
A Plugin extends ADK’s `BasePlugin` and implements callback hooks that run at key points of the **runner → agent → model/tool → events** lifecycle.  
Use Plugins for cross‑cutting concerns (logging, policy, metrics, caching, redaction). Prefer **agent callbacks** when the logic is specific to one agent.

**Why Plugins (vs. Callbacks)?**
- **Scope**: Register on the **Runner** once → applies to **all** agents/tools/models.
- **Precedence**: Plugin hooks run **before** Agent/Model/Tool callbacks.
- **Reuse**: Ship policies and utilities once; apply everywhere.

---

## Lifecycle Hooks (Plugins)

Return values control the flow:
- **Observe**: return `None` → let execution proceed.
- **Intervene**: return a value of the expected type → **short‑circuit** or **replace** the step.
- **Amend**: mutate provided context objects to tweak inputs/outputs.

| Stage | Hook (Python) | Purpose | Return type (to override) |
|---|---|---|---|
| User input | `on_user_message_callback(invocation_context, user_message)` | Inspect/replace the raw user message | `types.Content` |
| Runner start | `before_run_callback(invocation_context)` | Global setup per request | `types.Content` |
| Agent | `before_agent_callback(agent, callback_context)` / `after_agent_callback(agent, callback_context, content)` | Wrap agent’s main work | `types.Content` |
| Model | `before_model_callback(callback_context, llm_request)` / `after_model_callback(callback_context, llm_response)` / `on_model_error_callback(callback_context, llm_request, error)` | Pre/post LLM call; handle failures | `LlmResponse` |
| Tool | `before_tool_callback(tool, tool_args, tool_context)` / `after_tool_callback(tool, tool_args, tool_context, result)` / `on_tool_error_callback(tool, tool_args, tool_context, error)` | Validate/standardize tool I/O; handle failures | `dict` |
| Events | `on_event_callback(invocation_context, event)` | Inspect/modify streamed events | `Event` |
| Runner end | `after_run_callback(invocation_context)` | Cleanup/metrics flush | `None` |

**Precedence rule**: If a **Plugin** hook returns a non‑`None` value, the matching **Agent/Model/Tool** callback is **skipped** for that step.

---

## Project Layout

```
adk-plugins-guide/
├─ README.md
├─ main.py
├─ requirements.txt
└─ plugins/
   ├─ count_invocation_plugin.py
   ├─ cache_plugin.py
   ├─ tool_auth_plugin.py
   ├─ redact_pii_plugin.py
   └─ metrics_plugin.py
```

---

## Quickstart

```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The demo registers **all plugins** and runs a minimal agent/tool so you can see hook ordering, short‑circuiting, and event interception.

---

## Plugins Included

### 1) Invocation Counter
Counts agent runs and model calls — great to learn timing of hooks.

### 2) Model Response Cache
Implements a naive in‑memory cache via `before_model_callback` / `after_model_callback` to skip repeat LLM calls.

### 3) Tool Authorization
Blocks disallowed tools for the current session role using `before_tool_callback`.

### 4) PII Redaction
Sanitizes emails/phones inside streamed events via `on_event_callback`, so the UI never renders raw PII.

### 5) Prometheus Metrics
Exports counters/histograms for model/tool usage and latency.

---

## Demo Entrypoint (`main.py`)

- Registers all plugins.
- Creates a tiny function tool (`hello_world`) and runs a single turn.
- Prints events to stdout.

---

## Common Pitfalls

- **Web UI**: Not supported for plugins — use CLI/script.
- **Return types**: If you override a step, return the **exact** type ADK expects (`Content`, `LlmResponse`, `dict`, `Event`).
- **Precedence**: Plugin overrides **skip** matching agent/model/tool callbacks.
- **State**: Use `InvocationContext.session.state` to share policy/flags across hooks.

---

## Where to read more (official docs)
- **Plugins** overview, registration, hooks.
- **Callbacks** concepts and flow control via return types.

(Links are provided in the chat message that accompanies this download.)
