from typing import Dict
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

def generate_report(title: str, tool_context: ToolContext) -> Dict:
    report_text = f"# {title}\nThis is a generated report."
    report_part = types.Part.from_text(report_text)
    version = tool_context.save_artifact("report.md", report_part)

    # Read back / list files
    latest_notes = tool_context.load_artifact("notes.txt")
    names = tool_context.list_artifacts()

    return {
        "status": "ok",
        "saved_version": version,
        "has_notes": bool(latest_notes),
        "files": names,
    }

report_tool = FunctionTool(func=generate_report)

def main():
    agent = LlmAgent(
        name="artifact_agent",
        model="gemini-2.0-flash",
        instruction=(
            "When asked to generate a report, call the 'generate_report' tool and then"
            " tell the user which version you saved."
        ),
        tools=[report_tool],
    )

    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
    )

    # (This sample keeps it simple; integrate with your usual runner.run(...) flow)

if __name__ == "__main__":
    main()
