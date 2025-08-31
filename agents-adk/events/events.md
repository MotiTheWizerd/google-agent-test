# ADK Developer Guide — Events

A practical, code-first guide to **Events** in Google’s Agent Development Kit (ADK). Use this when wiring UIs, tools, and agents so your app reacts correctly to everything that happens in a conversation.

---

## 1) What is an Event?
**Event** is the atomic message ADK uses to move information and control through your system. Every user input, model output, tool call/result, state change, control signal, or error is represented as an `Event`.

Conceptually, an Event contains:
- **content**: the message payload (text, function calls, function responses, etc.)
- **metadata**: `author`, `invocation_id`, `id`, `timestamp`, `branch`
- **actions**: side‑effects & control: `state_delta`, `artifact_delta`, `transfer_to_agent`, `skip_summarization`, `escalate`, etc.

> Treat Events as an append‑only log for the current **Session**. The **Runner** commits each Event to history, applies `actions`, and then yields the processed Event back to your app/UI.

---

## 2) Common Event Shapes (JSON-ish)

### User input
```json
{
  "author": "user",
  "invocation_id": "inv-123",
  "content": {"parts": [{"text": "Book a flight to London"}]}
}
```

### LLM text (final)
```json
{
  "author": "TravelAgent",
  "content": {"parts": [{"text": "Sure — what’s your departure city?"}]},
  "partial": false,
  "turn_complete": true
}
```

### LLM streaming chunk (partial)
```json
{
  "author": "TravelAgent",
  "content": {"parts": [{"text": "S…"}]},
  "partial": true
}
```

### Tool call request (function_call)
```json
{
  "author": "TravelAgent",
  "content": {"parts": [{"function_call": {"name": "search_flights", "args": {"from": "TLV", "to": "LHR"}}}]}
}
```

### Tool result (function_response)
```json
{
  "author": "TravelAgent",
  "content": {"role": "user", "parts": [{"function_response": {"name": "search_flights", "response": {"flights": 42}}}]}
}
```

### Error
```json
{
  "author": "LLMAgent",
  "error_code": "SAFETY_FILTER_TRIGGERED",
  "error_message": "Response blocked due to safety settings."
}
```

### State/Artifact delta attached to next Event
```json
{
  "author": "TravelAgent",
  "content": {"parts": [{"text": "Saved your preference."}]},
  "actions": {
    "state_delta": {"user:home_airport": "TLV"},
    "artifact_delta": [{"op": "add", "key": "itinerary.pdf", "uri": "gcs://..."}]
  }
}
```

---

## 3) Event fields you’ll actually use
- `author`: `'user'` or an agent name (e.g., `WeatherAgent`)
- `content.parts`: list of parts (text | function_call | function_response | code, etc.)
- `partial`: `true` for streaming chunks
- `actions.state_delta`: key→value updates to commit into `session.state`
- `actions.artifact_delta`: references to files/blobs saved via context
- `actions.transfer_to_agent`: request a handoff to another agent
- `actions.skip_summarization`: hint the framework to skip auto‑summary
- `invocation_id`: groups all Events in one turn
- `id`, `timestamp`: unique event id + creation time

---

## 4) Event lifecycle — how they flow
1. **Generation**: Agents, tools, callbacks, and the model yield/emit Events.
2. **Runner processes** the Event:
   - merges `state_delta` / `artifact_delta` into the Session via the configured Services
   - appends the Event to `session.events`
   - yields the processed Event out to your app/UI
3. **Execution resumes**: Agent logic continues from where it yielded, now seeing committed state.

> Mental model: *yield → Runner commits → resume.*

---

## 5) Working with Events in Python

### 5.1 Subscribe to the event stream
```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.events import Event

session_service = InMemorySessionService()
runner = Runner(session_service=session_service)
session = Session(app_name="demo-app", user_id="moti", id="s1")

async def handle_query(query_text: str):
    # Send user message and run the agent tree
    async for event in runner.run_async(
        session=session,
        agent=root_agent,             # your BaseAgent/LlmAgent tree
        new_message=query_text,
    ):
        print(f"[{event.author}] partial={getattr(event, 'partial', None)}")

        # Streaming text
        if event.content and event.content.parts:
            part0 = event.content.parts[0]
            if getattr(part0, "text", None):
                if getattr(event, "partial", False):
                    ui.append_stream(part0.text)       # incremental render
                else:
                    ui.append_final(part0.text)

        # Tool requests → kick off tool execution (if you drive tools yourself)
        for fc in event.get_function_calls() or []:
            dispatch_tool(fc.name, fc.args)

        # Tool results → display or fold into the conversation view
        for fr in event.get_function_responses() or []:
            ui.show_tool_result(fr.name, fr.response)

        # Final response for this turn
        if event.is_final_response():
            ui.mark_turn_complete()
```

### 5.2 Emitting Events from a custom agent
```python
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai import types

class GreeterAgent(BaseAgent):
    name: str = "Greeter"

    async def _run_async_impl(self, ctx):
        # Example: persist a user preference before speaking
        actions = EventActions(state_delta={"user:preferred_name": "Moti"})

        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="Hey Moti! ")]),
            actions=actions,
        )

        # Follow-up message (final)
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="How can I help today?")]),
            # No actions here; state was already committed on previous yield
        )
```

### 5.3 Handling control signals and transfers
```python
from google.adk.events import Event, EventActions

# Ask the runtime to hand off to another agent
yield Event(
    author=self.name,
    actions=EventActions(transfer_to_agent="SearchAgent"),
)
```

### 5.4 Long‑running tools (pattern)
```python
# When a tool is declared long-running, ADK will emit a function_call event,
# return immediately, and later emit a function_response when the job completes.
# You consume both via the same event stream, keyed by function_call_id.
```

---

## 6) Java quick peek (minimal)
```java
Runner runner = new Runner(sessionService);
Flowable<Event> stream = runner.runAsync(session, rootAgent, userContent);

stream.subscribe(event -> {
  if (event.content().isPresent()) {
    var content = event.content().get();
    if (!event.functionCalls().isEmpty()) {
      // tool call
    } else if (!event.functionResponses().isEmpty()) {
      // tool result
    } else if (content.parts().isPresent() && !content.parts().get().isEmpty()) {
      var part0 = content.parts().get().get(0);
      part0.text().ifPresent(text -> ui.append(text));
    }
  }
  if (event.isFinalResponse()) {
    ui.markTurnComplete();
  }
});
```

---

## 7) Best practices
- **Use `is_final_response()`** to decide what to show as the completed answer for a turn.
- **Stream responsibly**: Accumulate partial text chunks only if you need the full string; otherwise render incrementally.
- **Keep authorship clean**: Always set `author=self.name` when your agent yields.
- **State vs content**: Put the human‑readable message in `content`; put side‑effects in `actions`.
- **Use prefixes for state scope** (`app:`, `user:`, `temp:`) if your SessionService supports them.
- **Trust the Runner**: Don’t manually persist deltas — yield an Event and let the Runner commit.

---

## 8) Troubleshooting
- **I don’t see my state change** → You updated `context.state` but didn’t yield an Event that carried the delta; changes are committed only when an Event is processed.
- **Tool result shows with role `user`** → That’s expected in LLM history; the Event `author` will still be your agent.
- **My UI shows partial gibberish** → Check `event.partial` and only render complete text for non‑streaming Events; otherwise stream progressively.

---

## 9) Quick checklist when wiring a UI
- Loop `async for event in runner.run_async(...)`
- Branch on **type**: user text / tool call / tool result / final
- Merge streaming text if needed
- React to `actions` (transfer, deltas) only through Runner’s processed Events
- Mark turn complete on `event.is_final_response()`

---

**Next chapter:** *Sessions* (state, history, persistence).

