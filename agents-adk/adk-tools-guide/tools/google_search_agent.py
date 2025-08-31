"""
Built-in tools sketch (Google Search / Code Execution):
Rules:
- One built-in per agent.
- Do not mix built-ins with other tools on the same agent.
- Compose multiple built-ins via Agent-as-a-Tool on a parent/root agent.
"""
# Pseudocode:
# from google.adk.tools import google_search
# search_agent = Agent(model="gemini-2.0-flash", name="searcher", instruction="Use Google Search to ground facts.", tools=[google_search])
