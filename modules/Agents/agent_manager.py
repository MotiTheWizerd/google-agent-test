from __future__ import annotations

from typing import Optional, Sequence

from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .env import load_env
from .team import configure_root


class AgentManager:
    """Manage and run ADK agent graphs."""

    def __init__(
        self,
        app_name: str = "adk_app",
        root_agent: Optional[BaseAgent] = None,
        sub_agents: Optional[Sequence[BaseAgent]] = None,
    ) -> None:
        load_env()
        self.app_name = app_name
        self.session_service = InMemorySessionService()
        self.root_agent = configure_root(root_agent, sub_agents)
        self.runner = Runner(
            agent=self.root_agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )

    async def run(self, user_input: str, session_id: str, user_id: str = "user") -> str:
        """Run the agent graph and return the final text response."""
        if not self.session_service.get_session(self.app_name, user_id, session_id):
            self.session_service.create_session(
                app_name=self.app_name, user_id=user_id, session_id=session_id
            )

        message = types.Content(parts=[types.Part(text=user_input)], role="user")
        final_text: str = ""
        async for event in self.runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            if event.content and event.content.parts:
                part = event.content.parts[0]
                text = getattr(part, "text", None)
                if text and event.partial:
                    print(text, end="", flush=True)
                elif text and event.is_final_response():
                    print(text, end="", flush=True)
                    final_text = text
        return final_text
