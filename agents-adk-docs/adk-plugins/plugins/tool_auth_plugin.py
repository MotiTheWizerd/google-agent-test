from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.tool_context import ToolContext
from typing import Any, Optional

class ToolAuthPlugin(BasePlugin):
    """Blocks tools not allowed for the user's role stored in session state."""
    def __init__(self, allowed_by_role: dict[str, set[str]]):
        super().__init__(name="tool_auth")
        self.allowed_by_role = allowed_by_role

    async def before_tool_callback(self, *, tool: Any, tool_args: dict[str, Any], tool_context: ToolContext) -> Optional[dict]:
        role = tool_context.invocation_context.session.state.get("role", "guest")
        tool_name = getattr(tool, "name", getattr(tool, "__name__", "unknown_tool"))
        allowed = self.allowed_by_role.get(role, set())
        if tool_name not in allowed:
            return {"error": f"Tool '{tool_name}' forbidden for role '{role}'."}
        return None
