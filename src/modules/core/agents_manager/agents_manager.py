"""Main agents manager for creating and executing dynamic agent flows."""

import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from google.adk.sessions import InMemorySessionService

from .agent_factory import AgentFactory
from .workflow_builder import WorkflowBuilder
from .agent_types import WorkflowConfig
from .workflow_manager import WorkflowManager
from .session_manager import SessionManager
from .runner_manager import RunnerManager
from .workflow_executor import WorkflowExecutor
from ...ui.terminal_ui_manager import TerminalUIManager

# Load environment variables
load_dotenv()


class AgentsManager:
    """Main manager for creating and executing dynamic agent flows."""
    
    def __init__(self, app_name: str = "agents_manager_app"):
        self.app_name = app_name
        self.agent_factory = AgentFactory()
        self.workflow_manager = WorkflowManager()
        self.session_service = InMemorySessionService()
        self.ui = TerminalUIManager()
        self.session_manager = SessionManager(self.session_service, self.ui)
        self.runner_manager = RunnerManager(self.app_name, self.session_service, self.ui)
        self.workflow_executor = WorkflowExecutor(self.agent_factory, self.runner_manager, self.ui)
    
    def register_tool(self, name: str, tool_func: callable) -> None:
        """Register a tool function with a name."""
        self.agent_factory.register_tool(name, tool_func)
    
    def register_agent(self, name: str, agent) -> None:
        """Register a pre-created agent."""
        self.agent_factory.register_agent(name, agent)
    
    def create_workflow_builder(self, name: str) -> WorkflowBuilder:
        """Create a new workflow builder."""
        return WorkflowBuilder(name)
    
    def register_workflow(self, workflow_config: WorkflowConfig) -> None:
        """Register a workflow configuration."""
        self.workflow_manager.register_workflow(workflow_config)
    
    def get_workflow(self, name: str) -> Optional[WorkflowConfig]:
        """Get a workflow configuration by name."""
        return self.workflow_manager.get_workflow(name)
    
    def list_workflows(self) -> List[str]:
        """List all registered workflow names."""
        return self.workflow_manager.list_workflows()
    
    async def run_workflow(self, 
                          workflow_name: str, 
                          input_text: str,
                          user_id: str = "default_user",
                          session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run a registered workflow with the given input."""
        if not self.workflow_manager.workflow_exists(workflow_name):
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflow_manager.get_workflow(workflow_name)
        
        # Get or create session
        session = await self.session_manager.get_or_create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Run the workflow
        return await self.workflow_executor.run_workflow(
            workflow=workflow,
            input_text=input_text,
            user_id=user_id,
            session=session
        )
    
    async def stream_workflow(self,
                             workflow_name: str,
                             input_text: str,
                             user_id: str = "default_user",
                             session_id: Optional[str] = None):
        """Stream a registered workflow with the given input.
        
        This method returns an async generator that yields events as they occur during
        workflow execution. Each event can be processed in real-time for streaming output.
        
        Args:
            workflow_name: Name of the workflow to run
            input_text: Input text for the workflow
            user_id: User ID for session management
            session_id: Session ID (optional, will create new if None)
            
        Yields:
            Events from the ADK Runner as they occur during workflow execution
        """
        if not self.workflow_manager.workflow_exists(workflow_name):
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflow_manager.get_workflow(workflow_name)
        
        # Get or create session
        session = await self.session_manager.get_or_create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Stream the workflow
        async for event in self.workflow_executor.stream_workflow(
            workflow=workflow,
            input_text=input_text,
            user_id=user_id,
            session=session
        ):
            yield event
    
    def print_workflow_info(self, workflow_name: str) -> None:
        """Print information about a registered workflow."""
        if not self.workflow_manager.workflow_exists(workflow_name):
            self.ui.print_error(f"Workflow '{workflow_name}' not found")
            return
        
        workflow = self.workflow_manager.get_workflow(workflow_name)
        
        # Get agent names for the table
        agent_names = [agent.name for agent in workflow.agents]
        
        # Print workflow info
        self.ui.print_workflow_info(workflow_name, workflow.description or "", agent_names)
        self.ui.print_info(f"Entry Point: {workflow.entry_point}")