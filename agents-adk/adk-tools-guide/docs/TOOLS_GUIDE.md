# Tools in Google ADK — Practical Guide

**What is a tool?** A structured, callable action exposed to the LLM: a function with typed params and a docstring that becomes the description. Return JSON‑like dicts with stable keys.

## Core patterns
- **Function tools:** regular Python functions auto‑wrapped by ADK. Keep names short and docstrings imperative.
- **Long‑running tools:** start a job, return a ticket, resume later.
- **Performance:** prefer `async def` and non‑blocking IO; yield during large loops.
- **Built‑ins:** Google Search / Code Execution / Vertex AI Search / BigQuery. **Rule:** one built‑in per agent; don’t mix with other tools on the same agent; compose via Agent‑as‑a‑Tool.
- **OpenAPI toolset:** turn an OpenAPI spec into tools with API Key/OAuth/OIDC/Service Account auth.
- **MCP:** use MCP servers as tools, or expose your ADK tools via MCP.
- **Third‑party wrappers:** CrewAI/LangChain/Tavily, Guardrails, etc.
- **Auth:** provide scheme + credential; interactive OAuth/OIDC uses a special `adk_request_credential` call to complete the browser flow.

## Return shape
Always include something like:
```json
{"status":"success","data":{...},"meta":{"source":"tool_name"}}
```
The LLM is text‑first; stable keys reduce reasoning errors.

## Prompting tips
- Tell the agent **when** to use a tool and **what** to return.
- Encourage **parallel** tool usage when safe: “Call multiple data sources in parallel and merge results.”
- In multi‑step plans, store interim values in the **turn‑local temp context** (available to all tools in the same turn).

## Safety foot‑guns
- Don’t mix built‑ins with other tools on one agent.
- Don’t block the event loop with CPU loops; chunk + yield.
- Don’t expose unvalidated user input to OpenAPI calls; validate/whitelist params.
