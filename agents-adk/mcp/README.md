# ADK + MCP Starter (Python)

This mini project shows how to use **Google Agent Development Kit (ADK)** with the **Model Context Protocol (MCP)** in two patterns:

1) **ADK as an MCP client** — connect your `LlmAgent` to an existing MCP server (filesystem and Google Maps examples).  
2) **Out of `adk web`** — a concise async pattern when you aren’t using the ADK web UI.

> Requires: Python 3.9+, Node.js (for `npx`), and the ADK + MCP Python packages.

---

## Project Tree

```
mcp-adk-starter/
└─ python/
   ├─ mcp_filesystem_agent/
   │  ├─ agent.py
   │  └─ __init__.py
   ├─ mcp_google_maps_agent/
   │  ├─ agent.py
   │  └─ __init__.py
   ├─ .env.example
   └─ requirements.txt
```

---

## 0) Install

```bash
# (Optional) create & activate venv
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install deps
pip install -r python/requirements.txt
```

You also need Node.js so `npx` can run community MCP servers (e.g., the filesystem and Google Maps MCP servers).

---

## 1) Filesystem MCP (ADK as MCP client)

This example connects your agent to the community **filesystem MCP server** using stdio via `npx`.

**Edit the path** in `python/mcp_filesystem_agent/agent.py` so it points to a real folder on your machine (absolute path).

Then launch the ADK web UI from the `python` folder’s parent:

```bash
cd python
adk web
```

In your browser, select **`filesystem_assistant_agent`** and try prompts like:

- “List files in the current directory.”  
- “Read the file `sample.txt`.”

---

## 2) Google Maps MCP (ADK as MCP client)

Set your API key in the shell or `.env`:

```bash
# Linux/macOS
export GOOGLE_MAPS_API_KEY="YOUR_KEY"
# Windows (PowerShell)
$env:GOOGLE_MAPS_API_KEY="YOUR_KEY"
```

Run ADK web:

```bash
cd python
adk web
```

Pick **`maps_assistant_agent`** and try:

- “Get directions from GooglePlex to SFO.”
- “Find coffee shops near Golden Gate Park.”

---

## 3) Using MCP tools outside `adk web` (async pattern)

When not using `adk web`, you typically create the MCP toolset & agent **asynchronously**, run once, then close the toolset. See the inline docstring in `mcp_filesystem_agent/agent.py` for a minimal pattern you can adapt.

---

## Security & deployment tips (high level)

- Prefer **`tool_filter`** to expose only the tools you actually need.
- For filesystem MCP, restrict to a known **allowed directory**.
- Set **timeouts** for MCP connections and calls; cleanly **close** toolsets.
- For production scale, remote MCP servers over **SSE/HTTP** are easier to autoscale than spawning local stdio processes.

---

## Notes

- These examples use the ADK `MCPToolset` to connect to MCP servers via **stdio** (local process launched with `npx`). You can also connect to remote servers using SSE/HTTP connection params.
- Code is intentionally compact and annotated so you can transplant it into your own agents quickly.
