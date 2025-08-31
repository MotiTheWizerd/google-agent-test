# ADK Developer Guide — Sessions & Memory (Python)

This is a practical, code‑first guide for **Sessions** (short‑term, per‑conversation context) and **Memory** (cross‑session, long‑term knowledge) using Google’s Agent Development Kit (ADK).

---

## 0) What you’re building

A minimal project that:
- Starts an ADK agent with a **SessionService** (in‑memory or Vertex AI).
- Uses **session.state** to track facts during a chat.
- Ingests a finished session into a **MemoryService**.
- Searches memory in later chats to personalize replies.

**Project layout**
```
adk-sessions-memory/
  ├─ app.py                # runnable demo (in‑memory services)
  ├─ app_vertex.py         # runnable demo (Vertex AI Sessions & Memory Bank)
  ├─ agents.py             # agents (capture + recall)
  ├─ tools.py              # memory search tool (optional)
  ├─ services.py           # factory: pick SessionService/MemoryService
  ├─ requirements.txt      # python deps
  └─ .env                  # only if you use Vertex AI Express Mode
```

---

## 1) Install

```
pip install google-adk
```

(Optional, for Vertex AI managed services)
```
pip install google-cloud-aiplatform vertexai
```

---

## 2) Core concepts in 30 seconds

- **Session** – one conversation thread. Holds chronological **events** and a scratchpad **state**.
- **SessionService** – creates, fetches, appends events to, lists, and deletes sessions.
- **session.state** – key→value store (strings/numbers/booleans/lists/dicts of simple types). Use it as the agent’s scratchpad.
- **MemoryService** – long‑term store you *search* later (in‑memory for prototyping, or **Vertex AI Memory Bank** for persistent, semantic memory).

---

## 3) Code: in‑memory Session + in‑memory Memory

**agents.py**
```python
from google.adk.agents import LlmAgent

MODEL = "gemini-2.0-flash"

# 1) Captures facts; saves its final text into session.state["last_fact"]
fact_captor = LlmAgent(
    name="FactCaptor",
    model=MODEL,
    instruction=(
        "Extract the user-provided fact and acknowledge it briefly."
        " Only respond with a short acknowledgement."
    ),
    output_key="last_fact",  # ADK writes the final response into session.state
)

# 2) Uses memory to answer questions across sessions
recall_agent = LlmAgent(
    name="RecallAgent",
    model=MODEL,
    instruction=(
        "Answer the user's question. If needed, call the load_memory tool"
        " to search across past sessions."
    ),
    tools=[],  # we'll attach the built-in tool via Runner (see app.py)
)
```

**services.py**
```python
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

# In-memory services: great for local dev; data is lost on restart
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
```

**app.py**
```python
import asyncio
from google.adk.runners import Runner
from google.adk.tools import load_memory  # built‑in tool to query MemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
from agents import fact_captor, recall_agent

APP = "adk_sessions_demo"
USER = "user_1"

async def main():
    # --- shared services across runs ---
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    # Turn 1: capture a fact in session S1
    runner1 = Runner(
        agent=fact_captor,
        app_name=APP,
        session_service=session_service,
        memory_service=memory_service,
        tools=[load_memory],  # available, though not needed in this turn
    )

    s1 = await session_service.create_session(app_name=APP, user_id=USER, session_id="S1")
    msg1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")

    async for event in runner1.run_async(user_id=USER, session_id=s1.id, new_message=msg1):
        if event.is_final_response():
            print("[Captor]", event.content.parts[0].text)

    # Ingest the completed session into long‑term memory
    completed_s1 = await session_service.get_session(APP, USER, s1.id)
    await memory_service.add_session_to_memory(completed_s1)

    # Turn 2: recall in a new session S2
    runner2 = Runner(
        agent=recall_agent,
        app_name=APP,
        session_service=session_service,
        memory_service=memory_service,
        tools=[load_memory],  # enable memory search for this agent
    )

    s2 = await session_service.create_session(app_name=APP, user_id=USER, session_id="S2")
    msg2 = Content(parts=[Part(text="What is my favorite project?")], role="user")

    async for event in runner2.run_async(user_id=USER, session_id=s2.id, new_message=msg2):
        if event.is_final_response():
            print("[Recall]", event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

**What’s happening**
- We run one session to **capture** info; ADK writes the reply into `state["last_fact"]` via `output_key`.
- We send that **session** into the **MemoryService**.
- In a new session, the agent **searches memory** (via `load_memory`) to answer cross‑session questions.

---

## 4) Working with `session.state` (cleanly)

Use the state as a scratchpad and let ADK track updates via events. Two ways you’ll actually use:

**(A) Store final LLM output into state (simplest)**
```python
from google.adk.agents import LlmAgent

prefs = LlmAgent(
    name="Prefs",
    model="gemini-2.0-flash",
    instruction="Ask the user for a preferred theme and store it.",
    output_key="user:theme",  # user‑scoped key persists across sessions (with persistent SessionService)
)
```

**(B) Apply a structured `state_delta` as part of an Event**
```python
import time
from google.adk.events import Event, EventActions

state_changes = {
    "task_status": "active",          # session‑scoped
    "user:login_count": 1,             # user‑scoped
    "temp:raw_api_response": {"ok": True},  # discarded after this invocation
}

actions = EventActions(state_delta=state_changes)
login_evt = Event(
    invocation_id=f"inv_{int(time.time())}",
    author="system",
    actions=actions,
)
# session_service.append_event(session, login_evt)  # Runner usually does this for you
```

**Templating `session.state` into instructions**
```python
from google.adk.agents import LlmAgent

story = LlmAgent(
    name="Story",
    model="gemini-2.0-flash",
    instruction="Write a {mood} story about a cat.",  # pulls from session.state["mood"]
)
```

**Good hygiene**
- Don’t mutate `Session.state` directly on a fetched session; update state via `output_key`, `EventActions.state_delta`, or context objects within callbacks/tools so ADK can persist and diff it.
- Use prefixes to scope: `user:` (per user), `app:` (global), `temp:` (per invocation), or none (per session).

---

## 5) Vertex AI managed Sessions & Memory (Express Mode or full GCP)

Switching from local/in‑memory to **managed** backends takes a few lines and gives you:
- Durable sessions across restarts & instances.
- **Semantic** long‑term memory (Memory Bank) generated from session transcripts.

**Prereqs (Express Mode quick path)**
```
# .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=PASTE_YOUR_EXPRESS_MODE_API_KEY
```

**app_vertex.py (sketch)**
```python
from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import load_memory

APP = "your_agent_engine_id"   # Parent of Session/Memory in Vertex AI
USER = "user_1"

session_service = VertexAiSessionService(project="PROJECT_ID", location="LOCATION")
memory_service  = VertexAiMemoryBankService(project="PROJECT_ID", location="LOCATION", agent_engine_id=APP)

agent = LlmAgent(
    name="Recall",
    model="gemini-2.0-flash",
    instruction="Use load_memory when relevant to answer across sessions.",
)

runner = Runner(
    agent=agent,
    app_name=APP,
    session_service=session_service,
    memory_service=memory_service,
    tools=[load_memory],
)

# Create a session, run, and let ADK persist to Vertex AI automatically.
```

**Notes**
- Express Mode is free but time‑limited; ideal for trying Vertex Sessions/Memory without a paid GCP project.
- With Vertex backends, you don’t babysit persistence—sessions & memories live server‑side and scale.

---

## 6) Patterns and tips

- **Share services**: use the *same* `SessionService`/`MemoryService` instances across runners if you want them to see the same state/memory in a process.
- **When to ingest**: call `add_session_to_memory(session)` when the chat hits a milestone or ends. For Vertex Memory Bank, ADK can automate extraction; you can still push specific sessions.
- **Guardrails**: keep state values JSON‑serializable; avoid giant blobs; store file data as **Artifacts** and reference them.
- **Prefixes = scope**: `user:` survives and applies across the user’s sessions (with persistent services); `temp:` is strictly per‑invocation.
- **Testing**: mock/replace services for unit tests (e.g., in‑memory for speed, Vertex for integration).

---

## 7) requirements.txt
```
google-adk
# Optional if using Vertex AI managed services
google-cloud-aiplatform
vertexai
```

---

## 8) Next steps (nice add‑ons)
- Add a small FastAPI to expose `/chat` that routes `session_id` and uses the same services.
- Wire **Artifacts** if you want durable files/images/audio linked to sessions or users.
- Stream responses with ADK’s `adk web` dev UI for faster iteration.

---

### Quick sanity checklist
- [ ] `pip show google-adk` shows a recent version.
- [ ] In‑memory demo runs and prints a recall using `load_memory`.
- [ ] Vertex demo authenticates and persists across restarts.
- [ ] You kept state small, typed, and prefixed where it matters.

