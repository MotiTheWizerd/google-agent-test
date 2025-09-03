"""Workflow executor for running agent workflows."""

from typing import Dict, Any, List, Optional
from google.genai import types
from .agent_factory import AgentFactory
from .runner_manager import RunnerManager
from ...ui.terminal_ui_manager import TerminalUIManager


class WorkflowExecutor:
    """Executor for running workflows and processing events."""
    
    def __init__(self, 
                 agent_factory: AgentFactory, 
                 runner_manager: RunnerManager, 
                 ui: TerminalUIManager):
        self.agent_factory = agent_factory
        self.runner_manager = runner_manager
        self.ui = ui
    
    async def run_workflow(self,
                          workflow,
                          input_text: str,
                          user_id: str,
                          session) -> Dict[str, Any]:
        """
        Run a workflow with the given input.
        
        Args:
            workflow: The workflow configuration
            input_text: The input text for the workflow
            user_id: The user ID
            session: The session object
            
        Returns:
            Dictionary containing results
        """
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
        runner = self.runner_manager.create_runner(entry_agent)
        
        # Prepare input message
        message = types.Content(
            parts=[types.Part(text=input_text)],
            role="user"
        )
        
        # Run the workflow
        self.ui.print_running_workflow(workflow.name, user_id, session.id)
        self.ui.print_input(input_text)
        
        results = {
            "events": [],
            "final_output": None,
            "session_state": {},
            "session_id": session.id,
            "user_id": user_id
        }
        
        # For streaming text output, we'll accumulate partial responses
        accumulated_text = ""
        
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=message
            ):
                results["events"].append(event)
                
                # Handle streaming text output
                if event.content and event.content.parts:
                    # Check if this is a partial response
                    if getattr(event, 'partial', False):
                        # For partial responses, accumulate and print incrementally
                        part0 = event.content.parts[0]
                        if hasattr(part0, 'text') and part0.text:
                            accumulated_text += part0.text
                            # Print the new text without a newline for streaming effect
                            self.ui.console.print(part0.text, end='', style=self.ui._get_color("agent"))
                    else:
                        # For complete responses, check if we have accumulated text
                        part0 = event.content.parts[0]
                        if hasattr(part0, 'text') and part0.text:
                            # If we have accumulated text, this might be the final part
                            if accumulated_text:
                                # Add the final part to accumulated text
                                accumulated_text += part0.text
                                # Print a newline to end the streaming output
                                self.ui.console.print("")  # New line after streaming
                                # Reset accumulated text
                                accumulated_text = ""
                            else:
                                # This is a complete response without streaming
                                self.ui.console.print(part0.text, style=self.ui._get_color("agent"))
                
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
    
    async def stream_workflow(self,
                             workflow,
                             input_text: str,
                             user_id: str,
                             session):
        """
        Stream a workflow with the given input.
        
        This method yields events as they occur during workflow execution,
        allowing for real-time processing of streaming output.
        
        Args:
            workflow: The workflow configuration
            input_text: The input text for the workflow
            user_id: The user ID
            session: The session object
            
        Yields:
            Events from the ADK Runner as they occur during workflow execution
        """
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
        runner = self.runner_manager.create_runner(entry_agent)
        
        # Prepare input message
        message = types.Content(
            parts=[types.Part(text=input_text)],
            role="user"
        )
        
        # Print workflow start info
        self.ui.print_running_workflow(workflow.name, user_id, session.id)
        self.ui.print_input(input_text)
        
        try:
            # Stream events from the runner
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=message
            ):
                # Handle streaming text output
                if event.content and event.content.parts:
                    # Check if this is a partial response
                    if getattr(event, 'partial', False):
                        # For partial responses, print incrementally
                        part0 = event.content.parts[0]
                        if hasattr(part0, 'text') and part0.text:
                            # Print the new text without a newline for streaming effect
                            self.ui.console.print(part0.text, end='', style=self.ui._get_color("agent"))
                    else:
                        # For complete responses, print with a newline
                        part0 = event.content.parts[0]
                        if hasattr(part0, 'text') and part0.text:
                            # Print a newline if we were streaming
                            if hasattr(event, 'partial') and event.partial:
                                self.ui.console.print("")  # New line after streaming
                            else:
                                self.ui.console.print(part0.text, style=self.ui._get_color("agent"))
                
                # Process and yield events for streaming
                # Print tool calls
                if hasattr(event, 'get_function_calls'):
                    for call in event.get_function_calls() or []:
                        self.ui.print_event({"type": "tool_call", "tool_call": {"name": call.name, "args": call.args}})
                
                # Print tool responses
                if hasattr(event, 'get_function_responses'):
                    for response in event.get_function_responses() or []:
                        self.ui.print_event({"type": "tool_response", "tool_response": {"name": response.name, "response": response.response}})
                
                # Yield the event for streaming processing
                yield event
                
        except Exception as e:
            self.ui.print_error(f"Error streaming workflow: {e}")
            raise