"""Agent types and configuration schemas for the agents manager."""

from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class AgentType(Enum):
    """Enumeration of supported agent types."""
    LLM = "llm"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"
    CUSTOM = "custom"


class BaseAgentConfig(BaseModel):
    """Base configuration for all agents."""
    name: str = Field(..., description="Unique name for the agent")
    description: Optional[str] = Field(None, description="Description of the agent's purpose")
    type: AgentType = Field(..., description="Type of agent to create")


class LlmAgentConfig(BaseAgentConfig):
    """Configuration for LLM agents."""
    model: str = Field(..., description="Gemini model to use (e.g., gemini-2.0-flash)")
    instruction: str = Field(..., description="System instruction for the agent")
    tools: List[str] = Field(default_factory=list, description="List of tool names to register with the agent")
    output_key: Optional[str] = Field(None, description="Key to store agent output in session state")
    include_contents: str = Field("default", description="Content inclusion strategy (default, none, all)")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Temperature for generation")
    max_output_tokens: int = Field(1024, description="Maximum output tokens")


class SequentialAgentConfig(BaseAgentConfig):
    """Configuration for sequential agents."""
    sub_agents: List[Union[str, dict]] = Field(..., description="List of sub-agent names or configurations")
    type: AgentType = AgentType.SEQUENTIAL


class ParallelAgentConfig(BaseAgentConfig):
    """Configuration for parallel agents."""
    sub_agents: List[Union[str, dict]] = Field(..., description="List of sub-agent names or configurations")
    type: AgentType = AgentType.PARALLEL


class LoopAgentConfig(BaseAgentConfig):
    """Configuration for loop agents."""
    sub_agents: List[Union[str, dict]] = Field(..., description="List of sub-agent names or configurations")
    max_iterations: int = Field(5, description="Maximum number of iterations")
    type: AgentType = AgentType.LOOP


# Union type for any agent configuration
AgentConfig = Union[
    LlmAgentConfig,
    SequentialAgentConfig,
    ParallelAgentConfig,
    LoopAgentConfig
]


class WorkflowConfig(BaseModel):
    """Configuration for a complete workflow."""
    name: str = Field(..., description="Unique name for the workflow")
    description: Optional[str] = Field(None, description="Description of the workflow")
    agents: List[AgentConfig] = Field(..., description="List of agent configurations")
    entry_point: str = Field(..., description="Name of the entry point agent")