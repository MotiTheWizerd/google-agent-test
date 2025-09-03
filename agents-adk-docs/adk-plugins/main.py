import asyncio
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Plugins
from plugins.count_invocation_plugin import CountInvocationPlugin
from plugins.cache_plugin import CachePlugin
from plugins.tool_auth_plugin import ToolAuthPlugin
from plugins.redact_pii_plugin import RedactPIIPlugin
from plugins.metrics_plugin import MetricsPlugin

async def hello_world(tool_context: ToolContext, query: str) -> dict:
    print(f"[tool:hello_world] query={query}")
    return {"ok": True, "echo": query}

async def main():
    agent = Agent(
        model="gemini-2.0-flash",
        name="hello_world_agent",
        description="Echoes a query via hello_world tool",
        instruction="Use hello_world to echo user text.",
        tools=[hello_world],
    )

    allow = {"admin": {"hello_world"}, "guest": set()}

    runner = InMemoryRunner(
        agent=agent,
        app_name="adk_plugins_demo",
        plugins=[
            CountInvocationPlugin(),
            CachePlugin(ttl_seconds=300, max_items=1024),
            ToolAuthPlugin(allowed_by_role=allow),
            RedactPIIPlugin(),
            MetricsPlugin(port=9100),
        ],
    )

    session = await runner.session_service.create_session(user_id="user", app_name="adk_plugins_demo")
    session.state["role"] = "admin"

    msg = types.Content(role="user", parts=[types.Part.from_text(text="hello +123-456-789")])

    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=msg):
        author = getattr(event, "author", "unknown")
        try:
            content = event.stringify_content()
        except Exception:
            content = str(getattr(event, "content", ""))
        print(f"[event] {author}: {content}")

if __name__ == "__main__":
    asyncio.run(main())
