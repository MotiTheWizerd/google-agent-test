from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

def main():
    agent = LlmAgent(
        name="artifact_quickstart",
        model="gemini-2.0-flash",
        instruction="You are quiet; artifact demo only."
    )

    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
    )

    # Build a text artifact
    hello = types.Part.from_text("hello artifacts")
    v = runner.artifact_service.save_artifact(
        app_name="artifact_app",
        user_id="u123",
        session_id="s123",
        filename="notes.txt",
        artifact=hello,
    )
    print("Saved notes.txt version:", v)

    # List files
    keys = runner.artifact_service.list_artifact_keys(
        app_name="artifact_app",
        user_id="u123",
        session_id="s123",
    )
    print("Keys:", keys)

    # Load latest
    loaded = runner.artifact_service.load_artifact(
        app_name="artifact_app",
        user_id="u123",
        session_id="s123",
        filename="notes.txt",
    )
    print("Loaded text:", loaded.text if loaded else None)

if __name__ == "__main__":
    main()
