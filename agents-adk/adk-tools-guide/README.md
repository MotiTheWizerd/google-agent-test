# Google ADK — Tools (Developer Guide + Examples)

This project is a **tools-first** starter for Google’s Agent Development Kit (ADK). It contains:
- A concise guide to tools in `docs/TOOLS_GUIDE.md`
- Minimal Python examples for function tools, long-running tools, OpenAPI tools, built-ins composition, and MCP/third‑party mappers.

> ⚠️ These examples are structured to match the ADK docs. They assume you have the ADK and its dependencies installed. Some import paths may change across ADK versions — cross‑check with the official docs at https://google.github.io/adk-docs/ before running.

## Structure
```
adk-tools-guide/
├─ app.py
├─ requirements.txt
├─ docs/
│  └─ TOOLS_GUIDE.md
└─ tools/
   ├─ simple_math.py
   ├─ long_running.py
   ├─ openapi_echo.py
   ├─ google_search_agent.py
   ├─ code_exec_agent.py
   ├─ mcp_client.py
   └─ third_party.py
```

## Quick start
1) Install Python 3.11+ and a fresh virtual environment.
2) Install ADK following the official docs (package name and extra deps may vary by release).
3) Read `docs/TOOLS_GUIDE.md` for concepts and the caveats (built‑in tool limits, auth patterns, async/parallelism).
4) Use the code files in `tools/` as reference when wiring your own agent.

## License
Unlicensed sample; use at your own risk.
