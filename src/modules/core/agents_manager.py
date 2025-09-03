"""Main agents manager for creating and executing dynamic agent flows."""

import asyncio
from typing import Dict, Any, List, Optional, Union
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent_factory import AgentFactory
from .workflow_builder import WorkflowBuilder
from .agent_types import (
    AgentConfig,
    WorkflowConfig,
    LlmAgentConfig,
    SequentialAgentConfig,
    ParallelAgentConfig,
    LoopAgentConfig
)
from ..ui.terminal_ui_manager import TerminalUIManager


class AgentsManager:
    """Main manager for creating and executing dynamic agent flows."""
    
    def __init__(self, app_name: str = "agents_manager_app"):
        self.app_name = app_name
        self.agent_factory = AgentFactory()
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.session_service = InMemorySessionService()
        self.ui = TerminalUIManager()
    
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
        self.workflows[workflow_config.name] = workflow_config
    
    def get_workflow(self, name: str) -> Optional[WorkflowConfig]:
        """Get a workflow configuration by name."""
        return self.workflows.get(name)
    
    def list_workflows(self) -> List[str]:
        """List all registered workflow names."""
        return list(self.workflows.keys())
    
    async def run_workflow(self, 
                          workflow_name: str, 
                          input_text: str,
                          user_id: str = "default_user",
                          session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run a registered workflow with the given input."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflows[workflow_name]
        
        # Create all agents in the workflow
        agents = {}
        for agent_config in workflow.agents:
            try:
                agent = self.agent_factory.create_agent(agent_config)
                agents[agent_config.name] = agent
            except Exception as e:
                self.ui.print_error(f"Error creating agent '{agent_config.name}': {e}")
                raise
        
        # Get entry point agent
        entry_agent = agents.get(workflow.entry_point)
        if not entry_agent:
            raise ValueError(f"Entry point agent '{workflow.entry_point}' not found")
        
        # Create runner
        runner = Runner(agent=entry_agent, app_name=self.app_name, session_service=self.session_service)
        
        # Create or get session
        session = None
        if session_id:
            # Try to get existing session
            try:
                session = await self.session_service.get_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                self.ui.print_session_creation("Retrieved existing session", session.id if session else None)
                # If session doesn't exist, create a new one
                if session is None:
                    self.ui.print_warning("Session not found, creating new one")
                    session = await self.session_service.create_session(
                        app_name=self.app_name,
                        user_id=user_id,
                        session_id=session_id
                    )
                    self.ui.print_session_creation("Created new session with provided ID", session.id if session else None)
            except Exception as e:
                # If there's an exception, create a new one
                self.ui.print_warning(f"Session not found or error occurred, creating new one: {e}")
                session = await self.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                self.ui.print_session_creation("Created new session with provided ID", session.id if session else None)
        else:
            # Create a new session
            try:
                session = await self.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_id
                )
                self.ui.print_session_creation("Created new session with generated ID", session.id if session else None)
            except Exception as e:
                self.ui.print_error(f"Error creating session: {e}")
                raise
        
        # Check if session was created successfully
        if session is None:
            raise ValueError("Failed to create or retrieve session")
        
        # Prepare input message
        message = types.Content(
            parts=[types.Part(text=input_text)],
            role="user"
        )
        
        # Run the workflow
        self.ui.print_running_workflow(workflow_name, user_id, session.id)
        self.ui.print_input(input_text)
        
        results = {
            "events": [],
            "final_output": None,
            "session_state": {},
            "session_id": session.id,
            "user_id": user_id
        }
        
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=message
            ):
                results["events"].append(event)
                
                # Print tool calls
                if hasattr(event, 'get_function_calls'):
                    for call in event.get_function_calls() or []:
                        self.ui.print_event({"type": "tool_call", "tool_call": {"name": call.name, "args": call.args}})
                
                # Print tool responses
                if hasattr(event, 'get_function_responses'):
                    for response in event.get_function_responses() or []:
                        self.ui.print_event({"type": "tool_response", "tool_response": {"name": response.name, "response": response.response}})
                
                # Capture final response
                if event.is_final_response() and event.content:
                    final_text = event.content.parts[0].text
                    results["final_output"] = final_text
                    self.ui.print_final_output(final_text)
        
            # Capture session state
            results["session_state"] = dict(session.state)
            
        except Exception as e:
            self.ui.print_error(f"Error running workflow: {e}")
            raise
        
        return results
    
    def print_workflow_info(self, workflow_name: str) -> None:
        """Print information about a registered workflow."""
        if workflow_name not in self.workflows:
            self.ui.print_error(f"Workflow '{workflow_name}' not found")
            return
        
        workflow = self.workflows[workflow_name]
        
        # Get agent names for the table
        agent_names = [agent.name for agent in workflow.agents]
        
        # Print workflow info
        self.ui.print_workflow_info(workflow_name, workflow.description or "", agent_names)
        self.ui.print_info(f"Entry Point: {workflow.entry_point}")