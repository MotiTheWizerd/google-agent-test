# ./python/mcp_filesystem_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# ⛔️ Replace this with an absolute path you want the filesystem MCP server to access.
# Example (Windows): r"C:\Users\me\Documents"
# Example (macOS/Linux): "/Users/me/Documents"
TARGET_FOLDER_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# --- LlmAgent wired to the MCP filesystem server via stdio (launched with npx) ---
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="filesystem_assistant_agent",
    instruction="Help the user manage files: list, read, search. Stay within the allowed directory.",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        TARGET_FOLDER_PATH,  # must be absolute
                    ],
                ),
                # Optional: timeout=5,
            ),
            # 🔐 Strongly recommended for production: expose only what you need
            # tool_filter=["list_directory", "read_file", "search_files", "directory_tree"],
        )
    ],
)

"""
Run in ADK Web:

    cd python
    adk web

Pick 'filesystem_assistant_agent' from the drop‑down and try:
  - "List files in the current directory."
  - "Read the file named sample.txt"

Out of adk web (async skeleton):

    import asyncio
    from google.genai import types
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService

    async def async_main():
        session_svc = InMemorySessionService()
        artifacts = InMemoryArtifactService()
        session = await session_svc.create_session(state={}, app_name="mcp_files", user_id="u1")

        content = types.Content(role="user", parts=[types.Part(text="list files")])
        runner = Runner(app_name="mcp_files", agent=root_agent, artifact_service=artifacts, session_service=session_svc)

        async for event in runner.run_async(session_id=session.id, user_id=session.user_id, new_message=content):
            print(event)

        # If you kept a handle to MCPToolset, close it:
        # await mcp_toolset.close()

    if __name__ == "__main__":
        asyncio.run(async_main())

"""

# Keep package importable for ADK discovery
# ./python/mcp_filesystem_agent/__init__.py will import this module
