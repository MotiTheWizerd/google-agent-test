"""
A tiny function tool the agent can call.
ADK wraps plain Python functions into FunctionTools automatically.
"""
from datetime import date

def hello(name: str) -> dict:
    today = date.today().isoformat()
    return {"greeting": f"Hello {name}!", "today": today}
