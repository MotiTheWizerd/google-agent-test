# ./python/mcp_google_maps_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Prefer setting GOOGLE_MAPS_API_KEY in your shell; falls back to .env if loaded by python-dotenv.
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

if not GOOGLE_MAPS_API_KEY:
    print("⚠ GOOGLE_MAPS_API_KEY is not set. Set it in your environment or a .env file.")

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="maps_assistant_agent",
    instruction="Use Google Maps MCP tools for directions and places.",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-google-maps",
                    ],
                    env={"GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY},
                ),
                # Optional: timeout=8,
            ),
            # tool_filter=["get_directions", "find_place_by_id"],
        )
    ],
)

"""
Run:

    # set your key first
    export GOOGLE_MAPS_API_KEY="YOUR_KEY"   # PowerShell: $env:GOOGLE_MAPS_API_KEY="YOUR_KEY"

    cd python
    adk web

Then select 'maps_assistant_agent' in the UI and try:
  - "Get directions from GooglePlex to SFO."
  - "Find coffee shops near Golden Gate Park."

"""
