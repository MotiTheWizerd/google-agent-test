"""Builder for creating agent workflows."""

from typing import List, Dict, Any, Optional, Union
from .agent_types import (
    AgentConfig,
    LlmAgentConfig,
    SequentialAgentConfig,
    ParallelAgentConfig,
    LoopAgentConfig,
    WorkflowConfig
)


class WorkflowBuilder:
    """Builder for creating agent workflows."""
    
    def __init__(self, name: str):
        self.name = name
        self.description: Optional[str] = None
        self.agents: List[AgentConfig] = []
        self.entry_point: Optional[str] = None
    
    def set_description(self, description: str) -> 'WorkflowBuilder':
        """Set the workflow description."""
        self.description = description
        return self
    
    def add_llm_agent(self, 
                      name: str,
                      model: str,
                      instruction: str,
                      description: Optional[str] = None,
                      tools: Optional[List[str]] = None,
                      output_key: Optional[str] = None,
                      include_contents: str = "default",
                      temperature: float = 0.7,
                      max_output_tokens: int = 1024) -> 'WorkflowBuilder':
        """Add an LLM agent to the workflow."""
        config = LlmAgentConfig(
            name=name,
            description=description,
            type="llm",
            model=model,
            instruction=instruction,
            tools=tools or [],
            output_key=output_key,
            include_contents=include_contents,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        self.agents.append(config)
        return self
    
    def add_sequential_agent(self,
                            name: str,
                            sub_agents: List[Union[str, dict]],
                            description: Optional[str] = None,
                            max_iterations: int = 5) -> 'WorkflowBuilder':
        """Add a sequential agent to the workflow."""
        config = SequentialAgentConfig(
            name=name,
            description=description,
            type="sequential",
            sub_agents=sub_agents
        )
        self.agents.append(config)
        return self
    
    def add_parallel_agent(self,
                          name: str,
                          sub_agents: List[Union[str, dict]],
                          description: Optional[str] = None) -> 'WorkflowBuilder':
        """Add a parallel agent to the workflow."""
        config = ParallelAgentConfig(
            name=name,
            description=description,
            type="parallel",
            sub_agents=sub_agents
        )
        self.agents.append(config)
        return self
    
    def add_loop_agent(self,
                      name: str,
                      sub_agents: List[Union[str, dict]],
                      description: Optional[str] = None,
                      max_iterations: int = 5) -> 'WorkflowBuilder':
        """Add a loop agent to the workflow."""
        config = LoopAgentConfig(
            name=name,
            description=description,
            type="loop",
            sub_agents=sub_agents,
            max_iterations=max_iterations
        )
        self.agents.append(config)
        return self
    
    def set_entry_point(self, agent_name: str) -> 'WorkflowBuilder':
        """Set the entry point agent for the workflow."""
        self.entry_point = agent_name
        return self
    
    def build(self) -> WorkflowConfig:
        """Build and return the workflow configuration."""
        if not self.entry_point:
            raise ValueError("Entry point must be set for the workflow")
        
        # Verify that entry point agent exists
        agent_names = [agent.name for agent in self.agents]
        if self.entry_point not in agent_names:
            raise ValueError(f"Entry point agent '{self.entry_point}' not found in workflow agents")
        
        return WorkflowConfig(
            name=self.name,
            description=self.description,
            agents=self.agents,
            entry_point=self.entry_point
        )