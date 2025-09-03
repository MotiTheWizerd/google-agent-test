from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name='basic_search_agent',
    model='gemini-2.0-flash-live-001',
    description='Answers with grounded facts via Google Search.',
    instruction='You are an expert researcher. Be concise and factual.',
    tools=[google_search],
)
