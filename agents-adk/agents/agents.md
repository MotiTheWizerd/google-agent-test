# Google ADK — Agents (Python)

A compact, implementation‑ready guide to building **agents** with Google’s Agent Development Kit (ADK), with runnable Python examples. Written so an AI agent (or a human) can follow it step‑by‑step.

---
## 0) Install & Project Setup

**Requirements**: Python 3.9+.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install google-adk python-dotenv pydantic
```

Create a project structure:

```
adk_agents/
  .env
  main.py
  agents/
    __init__.py
    capital_agent.py
    workflows.py
    custom.py
```

**.env** (AI Studio key example):
```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=PASTE_YOUR_KEY
```

> For Vertex AI instead of AI Studio: set `GOOGLE_GENAI_USE_VERTEXAI=TRUE` and provide `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.

---
## 1) LLM Agents — the core thinking unit

`LlmAgent` (aliased here as `Agent`) is the LLM‑powered component that reads context, decides, and optionally calls tools.

### 1.1 Minimal agent
```python
# agents/capital_agent.py
from google.adk.agents import LlmAgent as Agent

capital_agent = Agent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers: what's the capital of a given country?",
    instruction=(
        "You return the capital of a country.\n"
        "1) Identify the country. 2) If needed use tools. 3) Answer clearly."
    ),
)
```

### 1.2 Tools — give the agent real capabilities
Tool functions are just **typed Python functions**; ADK auto‑wraps them and exposes a JSON schema to the LLM.

```python
# agents/capital_agent.py (continue)
from typing import Dict

def get_capital_city(country: str) -> str:
    """Return the capital of a country."""
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Unknown capital for {country}.")

capital_tool_agent = Agent(
    model="gemini-2.0-flash",
    name="capital_tool_agent",
    description="Capital lookup using a function tool.",
    instruction=(
        "When asked for a capital, call get_capital_city(country) and then answer."
    ),
    tools=[get_capital_city],
)
```

**Tips**
- Add docstrings; the LLM reads them.
- Use precise type hints (`str`, `int`, `dict`); they shape the tool schema.

### 1.3 Control generation and structure
```python
from google.genai import types
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent as Agent

class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital city.")

structured_agent = Agent(
    model="gemini-2.0-flash",
    name="capital_structured",
    instruction=(
        "Return ONLY JSON: {\"capital\": \"<name>\"}."
    ),
    output_schema=CapitalOutput,    # enforce JSON shape
    output_key="found_capital",    # saves final text to session.state["found_capital"]
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, max_output_tokens=250
    ),
)
```

### 1.4 Context control — `include_contents`
By default, ADK includes relevant chat history. For stateless behavior:
```python
stateless_agent = Agent(
    model="gemini-2.0-flash",
    name="capital_stateless",
    instruction="Answer without referring to chat history.",
    include_contents="none",
)
```

### 1.5 Planner (optional) — multi‑step reasoning
Two options:
- **BuiltInPlanner** (uses model’s native “thinking”/planning if available)
- **PlanReActPlanner** (forces Plan → Act → Reason → Final Answer format)

```python
from google.adk.planners import BuiltInPlanner, PlanReActPlanner
from google.genai.types import ThinkingConfig

plan_agent = Agent(
    model="gemini-2.5-pro-preview-03-25",
    name="capital_planner",
    instruction="Plan, then answer about capitals.",
    planner=BuiltInPlanner(
        thinking_config=ThinkingConfig(include_thoughts=True, thinking_budget=256)
    ),
    tools=[get_capital_city],
)

react_agent = Agent(
    model="gemini-2.0-flash",
    name="capital_react",
    instruction="Use Plan/Act/Reason/Final format.",
    planner=PlanReActPlanner(),
    tools=[get_capital_city],
)
```

---
## 2) Workflow Agents — deterministic control flow

Use these to orchestrate multiple child agents.

### 2.1 SequentialAgent
Runs child agents one after another, sharing `session.state`.
```python
# agents/workflows.py
from google.adk.agents import SequentialAgent, LlmAgent as Agent

fetch = Agent(name="Step1_Fetch", model="gemini-2.0-flash", output_key="data")
process = Agent(name="Step2_Process", model="gemini-2.0-flash",
                instruction="Process: {data}")

pipeline = SequentialAgent(name="Pipeline", sub_agents=[fetch, process])
```

### 2.2 ParallelAgent
Executes sub‑agents concurrently; use distinct state keys.
```python
from google.adk.agents import ParallelAgent, LlmAgent as Agent

w = Agent(name="Weather", output_key="weather")
n = Agent(name="News", output_key="news")

gather = ParallelAgent(name="Gather", sub_agents=[w, n])
```

### 2.3 LoopAgent
Repeats sub‑agents until `max_iterations` or an event escalates.
```python
from google.adk.agents import LoopAgent, BaseAgent, LlmAgent as Agent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

class CheckDone(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        done = ctx.session.state.get("done", False)
        yield Event(author=self.name, actions=EventActions(escalate=bool(done)))

worker = Agent(name="Worker")  # may set state["done"] = True eventually
poller = LoopAgent(name="Poll", max_iterations=10, sub_agents=[worker, CheckDone(name="Checker")])
```

---
## 3) Multi‑Agent Systems — composition patterns

### 3.1 Hierarchy (parent with `sub_agents`)
```python
from google.adk.agents import LlmAgent as Agent

greeter = Agent(name="Greeter", model="gemini-2.0-flash")
coordinator = Agent(name="Coordinator", model="gemini-2.0-flash", sub_agents=[greeter])
```

### 3.2 Agent‑as‑Tool (`AgentTool`)
Make one agent callable as a tool from another.
```python
from google.adk.tools import agent_tool
from google.adk.agents import LlmAgent as Agent

summarizer = Agent(name="Summarizer", description="Summarizes text.")
summarizer_tool = agent_tool.AgentTool(agent=summarizer)

router = Agent(
    name="Router",
    model="gemini-2.0-flash",
    instruction="Use the Summarizer tool when asked to condense text.",
    tools=[summarizer_tool],
)
```

> Alternative: keep agents in `sub_agents` and let the LLM use **transfer_to_agent** implicitly when the coordinator’s instruction describes who does what.

---
## 4) Run it locally (Runner + Session)

Use the **Runner** with an in‑memory session service for fast local loops.

```python
# main.py
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.capital_agent import capital_tool_agent

load_dotenv()

APP = "adk_agents"
USER = "moti"
SESSION = "dev"

session_svc = InMemorySessionService(dev_ui=True)
session_svc.create_session(app_name=APP, user_id=USER, session_id=SESSION)

runner = Runner(agent=capital_tool_agent, app_name=APP, session_service=session_svc)

msg = types.Content(parts=[types.Part(text="What's the capital of Japan?")], role="user")
for event in runner.run(user_id=USER, session_id=SESSION, new_message=msg):
    # Print only the final answer
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
```

Run:
```bash
python main.py
```

> Set `dev_ui=True` to launch the interactive web Dev UI while running locally.

---
## 5) Practical Notes & Gotchas

- **Model names**: Pick a supported Gemini model string (e.g., `gemini-2.0-flash`, `gemini-2.5-pro-preview-03-25`).
- **Tools**: Return simple JSON‑serializable objects. Keep param names/descriptions clean; the LLM relies on them.
- **State passing**: Use `output_key` to stash structured outputs into `session.state` for the next agent.
- **Stateless turns**: Use `include_contents='none'` when you want a clean, history‑free decision.
- **Loops**: Exit by emitting an Event with `EventActions(escalate=True)` or hitting `max_iterations`.
- **Planner**: BuiltInPlanner exposes thoughts (if enabled). Don’t expose `include_thoughts=True` to end users unless you mean to.

---
## 6) Quick API Cheatsheet

- `LlmAgent(name, model, instruction, tools=[...], include_contents, output_schema, output_key, planner, ...)`
- `SequentialAgent(name, sub_agents=[...])`
- `ParallelAgent(name, sub_agents=[...])`
- `LoopAgent(name, sub_agents=[...], max_iterations=n)`
- `Runner(agent, app_name, session_service)` + `InMemorySessionService(dev_ui=True)`
- `AgentTool(agent=<BaseAgent>)` to call one agent from another as a tool.

---
### Ready‑to‑Fork Mini Example

A minimal repo with just a tool‑using LLM agent:

```
.
├─ .env
├─ main.py
└─ agents/
   ├─ __init__.py
   └─ capital_agent.py
```

**agents/capital_agent.py** — (same as 1.2)

**main.py** — (same as §4)

This runs out of the box after installing `google-adk` and setting the `.env`. Next step is to add workflows (sequential/parallel/loop) or compose multi‑agent patterns as shown above.

