from google.adk.agents import Agent
from . import __init__ as _pkg  # noqa: F401
from ..tools.hello_tool import hello

# Simple LLM agent that can call our hello() tool.
root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction=(
        "You are a friendly assistant. When the user provides a name, "
        "call the 'hello' tool and return the greeting."
    ),
    tools=[hello],
)
