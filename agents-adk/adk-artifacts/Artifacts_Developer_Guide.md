# Artifacts — Developer Guide (ADK)

> Pragmatic notes for using **artifacts** with agents, tools, and callbacks.

## What are Artifacts?
**Artifacts** are *named, versioned binary blobs* (files, images, audio, PDFs, CSVs, etc.) stored by an **ArtifactService** and scoped to a **session** (default) or **user** (“`user:`” prefix). They use the standard `google.genai.types.Part` (Python) / `com.google.genai.types.Part` (Java) container with `inline_data` (bytes + MIME type).

Typical use-cases:
- Persist generated files (reports, charts, audio)
- Handle user uploads
- Cache expensive binary results
- Share data across steps/agents; optionally across sessions (user namespace)

## Core pieces
- **BaseArtifactService**: abstract interface. Implementations:
  - `InMemoryArtifactService` — local/dev/testing
  - `GcsArtifactService` — persistent storage in Google Cloud Storage (GCS)
- **Context methods** (in tools/callbacks): `list_artifacts()`, `load_artifact(name, version=None)`, `save_artifact(name, part)`
- **Events**: when artifacts are saved, the event contains an `artifact_delta` you can observe for UI/telemetry.
- **Runner config**: provide `artifact_service` to your `Runner`. Without it, calls to `context.save_artifact(...)` will fail.

## Namespacing & versioning
- **Session scope** (default): `report.pdf`
- **User scope**: prefix with `user:` — `user:profile.png`
- **Versioning**: each save bumps an integer version starting from `0`; `save_artifact(...)` returns the new version. `load_artifact(name)` without `version` returns the latest.

## Python quickstart
```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

if __name__ == "__main__":
    # Minimal agent (no tools needed for this demo)
    agent = LlmAgent(name="artifact_demo", model="gemini-2.0-flash", instruction="Be quiet; this is a storage demo.")

    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
    )

    # Build a Part (blob) — here we use text; could be bytes for images, PDFs, etc.
    part = types.Part.from_text("hello artifacts")

    # Save (session-scoped)
    version = runner.artifact_service.save_artifact(
        app_name="artifact_app", user_id="u123", session_id="s123",
        filename="notes.txt", artifact=part
    )
    print("Saved 'notes.txt' version:", version)

    # List keys
    keys = runner.artifact_service.list_artifact_keys(
        app_name="artifact_app", user_id="u123", session_id="s123"
    )
    print("Keys:", keys)

    # Load latest
    loaded = runner.artifact_service.load_artifact(
        app_name="artifact_app", user_id="u123", session_id="s123",
        filename="notes.txt"
    )
    print("Loaded text:", loaded.text if loaded else None)

    # Save a user-scoped artifact (share across sessions)
    avatar = types.Part.from_bytes(b"...png-bytes...", mime_type="image/png")
    v2 = runner.artifact_service.save_artifact(
        app_name="artifact_app", user_id="u123", session_id="s123",
        filename="user:avatar.png", artifact=avatar
    )
    print("Saved 'user:avatar.png' version:", v2)
```

### Using artifacts inside a Tool (preferred)
Inside a tool function accept `tool_context: ToolContext` to access convenience methods:

```python
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types

def generate_report(title: str, tool_context: ToolContext) -> dict:
    # 1) Compute / render something (placeholder here)
    report_text = f"# {title}\nThis is a generated report."
    report_part = types.Part.from_text(report_text)

    # 2) Save it as an artifact (returns int version)
    version = tool_context.save_artifact("report.md", report_part)

    # 3) Optionally read previous files, or list available ones
    latest_notes = tool_context.load_artifact("notes.txt")        # version=None => latest
    all_files = tool_context.list_artifacts()                     # ['notes.txt', 'report.md', ...]

    # (Optional) signal the UI via event actions, etc.
    return {"status": "ok", "saved_version": version, "files": all_files}

report_tool = FunctionTool(func=generate_report)
```

### In callbacks (before/after agent/tool)
The convenience methods are also exposed on `CallbackContext`:
```python
def after_tool(callback_context, tool_name: str, tool_result: dict):
    # Mirror the generated result into an artifact for auditing
    result_part = types.Part.from_text(json.dumps(tool_result))
    callback_context.save_artifact(f"tool-{tool_name}-result.json", result_part)
```

## Java snippets
```java
import com.google.adk.runner.Runner;
import com.google.adk.agents.LlmAgent;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.artifacts.InMemoryArtifactService;
import com.google.genai.types.Part;

var agent = LlmAgent.builder()
    .name("artifact_demo")
    .model("gemini-2.0-flash")
    .instruction("Be quiet; this is a storage demo.")
    .build();

var runner = new Runner(agent, "artifact_app", new InMemoryArtifactService(), new InMemorySessionService());

Part part = Part.fromText("hello artifacts");
int version = runner.artifactService().saveArtifact(
    /* appName */ "artifact_app",
    /* userId */ "u123",
    /* sessionId */ "s123",
    /* filename */ "notes.txt",
    /* artifact */ part
);
System.out.println("Saved notes.txt version: " + version);
```

## Best practices
- **Always set `mime_type`** when using bytes. Use correct content types (`image/png`, `application/pdf`, `text/csv`, etc.).
- **Keep filenames stable** (e.g., `report.md`); rely on *versions* for history.
- **Use `user:` for cross-session needs**; default session scope for turn-local files.
- **Observe `artifact_delta`** on events for UI refresh and telemetry.
- **GCS for persistence**: in production, use `GcsArtifactService(bucket_name=...)`.

## Troubleshooting
- Missing `artifact_service` on your `Runner` → artifact methods in context will fail.
- Version confusion → print the return value from `save_artifact(...)` and/or call `list_versions(...)`.
- Large text files → prefer `Part.from_bytes(..., 'text/plain')` over `.from_text()` if you hit encoding edge-cases.
