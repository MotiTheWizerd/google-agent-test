# Events & Streaming

Running an agent produces a **stream of `Event`s**. In Python, iterate `async for event in runner.run_async(...)` and render progressively. Detect completion with `event.is_final_response()`. citeturn6view0

Minimal loop (see `src/run_local_async.py`):
```python
events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
async for event in events:
    if event.content and event.content.parts:
        # Render partial text
        text = ''.join(part.text or '' for part in event.content.parts)
        if text:
            print(text, end='', flush=True)
    if event.is_final_response():
        print("\n[final]")
```
