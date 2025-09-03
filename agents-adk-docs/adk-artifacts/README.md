# ADK Artifacts Starter

A tiny, self-contained starter for working with **Artifacts** in Google's **Agent Development Kit (ADK)**.

## What's inside
- `docs/Artifacts_Developer_Guide.md` — a practical walkthrough of Artifacts in ADK.
- `examples/python/artifacts_quickstart.py` — minimal save/load/list demo.
- `examples/python/artifacts_in_tool.py` — use artifacts inside a tool via `ToolContext`.
- `examples/java/ArtifactQuickstart.java` — quick Java example.

## Requirements
- Python 3.10+ (recommended)
- Java 17+ (for the Java example)
- ADK: `pip install google-adk`

## Run (Python quickstart)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install google-adk
python examples/python/artifacts_quickstart.py
```

If you use the Java example, import it into your IDE and add ADK Java deps per the official docs.
