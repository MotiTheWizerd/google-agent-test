"""Factory for creating different types of agents based on configuration."""

import asyncio
from typing import Dict, Any, List, Union, Optional
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
from google.adk.tools import FunctionTool
from .agent_types import (
    AgentType, 
    LlmAgentConfig, 
    SequentialAgentConfig, 
    ParallelAgentConfig, 
    LoopAgentConfig,
    AgentConfig
)


class AgentFactory:
    """Factory for creating agents based on configuration."""
    
    def __init__(self):
        self._tools_registry: Dict[str, callable] = {}
        self._agents_registry: Dict[str, BaseAgent] = {}
    
    def register_tool(self, name: str, tool_func: callable) -> None:
        """Register a tool function with a name."""
        self._tools_registry[name] = tool_func
    
    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Register a pre-created agent."""
        self._agents_registry[name] = agent
    
    def create_agent(self, config: AgentConfig) -> BaseAgent:
        """Create an agent based on the provided configuration."""
        # If agent is already registered, return it
        if config.name in self._agents_registry:
            return self._agents_registry[config.name]
        
        # Create agent based on type
        if config.type == AgentType.LLM:
            return self._create_llm_agent(config)
        elif config.type == AgentType.SEQUENTIAL:
            return self._create_sequential_agent(config)
        elif config.type == AgentType.PARALLEL:
            return self._create_parallel_agent(config)
        elif config.type == AgentType.LOOP:
            return self._create_loop_agent(config)
        else:
            raise ValueError(f"Unsupported agent type: {config.type}")
    
    def _create_llm_agent(self, config: LlmAgentConfig) -> LlmAgent:
        """Create an LLM agent from configuration."""
        # Resolve tools from registry
        tools = []
        for tool_name in config.tools:
            if tool_name in self._tools_registry:
                tools.append(self._tools_registry[tool_name])
            else:
                raise ValueError(f"Tool '{tool_name}' not found in registry")
        
        # Create the agent
        agent = LlmAgent(
            model=config.model,
            name=config.name,
            description=config.description or "",
            instruction=config.instruction,
            tools=tools,
            output_key=config.output_key,
            include_contents=config.include_contents
        )
        
        # Store in registry
        self._agents_registry[config.name] = agent
        return agent
    
    def _create_sequential_agent(self, config: SequentialAgentConfig) -> SequentialAgent:
        """Create a sequential agent from configuration."""
        sub_agents = self._resolve_sub_agents(config.sub_agents)
        
        agent = SequentialAgent(
            name=config.name,
            description=config.description or "",
            sub_agents=sub_agents
        )
        
        self._agents_registry[config.name] = agent
        return agent
    
    def _create_parallel_agent(self, config: ParallelAgentConfig) -> ParallelAgent:
        """Create a parallel agent from configuration."""
        sub_agents = self._resolve_sub_agents(config.sub_agents)
        
        agent = ParallelAgent(
            name=config.name,
            description=config.description or "",
            sub_agents=sub_agents
        )
        
        self._agents_registry[config.name] = agent
        return agent
    
    def _create_loop_agent(self, config: LoopAgentConfig) -> LoopAgent:
        """Create a loop agent from configuration."""
        sub_agents = self._resolve_sub_agents(config.sub_agents)
        
        agent = LoopAgent(
            name=config.name,
            description=config.description or "",
            sub_agents=sub_agents,
            max_iterations=config.max_iterations
        )
        
        self._agents_registry[config.name] = agent
        return agent
    
    def _resolve_sub_agents(self, sub_agents_config: List[Union[str, dict]]) -> List[BaseAgent]:
        """Resolve sub-agents from names or configurations."""
        sub_agents = []
        for item in sub_agents_config:
            if isinstance(item, str):
                # Item is a name, look it up in registry
                if item in self._agents_registry:
                    sub_agents.append(self._agents_registry[item])
                else:
                    raise ValueError(f"Sub-agent '{item}' not found in registry")
            elif isinstance(item, dict):
                # Item is a config dict, create agent from it
                # This would require parsing the dict into a config object
                # For simplicity, we'll assume it's already been resolved
                raise NotImplementedError("Creating agents from dict configs not yet implemented")
            else:
                raise ValueError(f"Invalid sub-agent configuration: {item}")
        
        return sub_agents