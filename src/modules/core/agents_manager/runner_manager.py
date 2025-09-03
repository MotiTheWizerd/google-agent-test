"""Runner manager for creating and managing agent runners."""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from ...ui.terminal_ui_manager import TerminalUIManager


class RunnerManager:
    """Manager for runner creation and management."""
    
    def __init__(self, app_name: str, session_service: InMemorySessionService, ui: TerminalUIManager):
        self.app_name = app_name
        self.session_service = session_service
        self.ui = ui
    
    def create_runner(self, agent) -> Runner:
        """
        Create a runner for the given agent.
        
        Args:
            agent: The agent to run
            
        Returns:
            Runner instance
        """
        return Runner(
            agent=agent, 
            app_name=self.app_name, 
            session_service=self.session_service
        )