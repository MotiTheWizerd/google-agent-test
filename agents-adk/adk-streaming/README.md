# ADK Streaming Developer Docs (Mini Project)

Practical, copy‑pasteable notes for building **bidirectional streaming** with Google's Agent Development Kit (ADK).

**What’s inside**
- `docs/streaming.md` — end‑to‑end guide: setup, live sessions, RunConfig, SSE/WebSockets, streaming tools.
- `examples/python/live_text_stream.py` — minimal text streaming loop with `run_live()`.
- `examples/python/live_audio_stream_ws_server.py` — FastAPI WebSocket server that relays text/audio ⇄ ADK.
- `examples/python/streaming_tools_demo.py` — define an async streaming tool and react to intermediate yields.

> Tested against `google-adk` 1.10.x style APIs. Adjust model IDs to current **Gemini Live** model names as needed.
