import asyncio
from typing import AsyncGenerator
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.agents import LiveRequestQueue

async def monitor_stock(ticker: str) -> AsyncGenerator[str, None]:
    for price in [300, 400, 900, 500]:
        await asyncio.sleep(2)
        yield f"{ticker} -> {price}"

def stop_streaming(function_name: str):
    """Hook for stopping a streaming tool by name (implement your own registry)."""
    pass

root_agent = Agent(
    name="streaming_tools_agent",
    model="gemini-2.0-flash-live-001",
    instruction=(
        "Use monitor_stock to watch a ticker. Read its streamed values and speak when a price changes materially."
    ),
    tools=[monitor_stock, FunctionTool(stop_streaming)]
)

# You can now run this agent with run_live(...), ask it to 'monitor AAPL', and it will react as yields arrive.