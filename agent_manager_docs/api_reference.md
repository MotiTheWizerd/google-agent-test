# API Reference

This document provides detailed information about the classes, methods, and functions available in the Agents Manager module.

## AgentsManager

The main orchestrator class for managing agents and workflows.

### Constructor

```python
AgentsManager(app_name: str = "agents_manager_app")
```

**Parameters:**
- `app_name` (str): The name of the application for session management

### Methods

#### register_tool

```python
register_tool(name: str, tool_func: callable) -> None
```

Register a tool function with a name.

**Parameters:**
- `name` (str): The name to register the tool under
- `tool_func` (callable): The function to register as a tool

#### register_agent

```python
register_agent(name: str, agent) -> None
```

Register a pre-created agent.

**Parameters:**
- `name` (str): The name to register the agent under
- `agent`: The agent instance to register

#### create_workflow_builder

```python
create_workflow_builder(name: str) -> WorkflowBuilder
```

Create a new workflow builder.

**Parameters:**
- `name` (str): The name for the new workflow

**Returns:**
- `WorkflowBuilder`: A new workflow builder instance

#### register_workflow

```python
register_workflow(workflow_config: WorkflowConfig) -> None
```

Register a workflow configuration.

**Parameters:**
- `workflow_config` (WorkflowConfig): The workflow configuration to register

#### get_workflow

```python
get_workflow(name: str) -> Optional[WorkflowConfig]
```

Get a workflow configuration by name.

**Parameters:**
- `name` (str): The name of the workflow to retrieve

**Returns:**
- `Optional[WorkflowConfig]`: The workflow configuration or None if not found

#### list_workflows

```python
list_workflows() -> List[str]
```

List all registered workflow names.

**Returns:**
- `List[str]`: A list of registered workflow names

#### run_workflow

```python
async run_workflow(workflow_name: str, input_text: str, user_id: str = "default_user", session_id: Optional[str] = None) -> Dict[str, Any]
```

Run a registered workflow with the given input.

**Parameters:**
- `workflow_name` (str): The name of the workflow to run
- `input_text` (str): The input text for the workflow
- `user_id` (str): The user ID for session management
- `session_id` (Optional[str]): The session ID (optional, will create new if None)

**Returns:**
- `Dict[str, Any]`: A dictionary containing the results with keys:
  - `events`: List of events generated during execution
  - `final_output`: The final output text
  - `session_state`: The final session state
  - `session_id`: The session ID used
  - `user_id`: The user ID used

**Raises:**
- `ValueError`: If the workflow is not found

#### print_workflow_info

```python
print_workflow_info(workflow_name: str) -> None
```

Print information about a registered workflow.

**Parameters:**
- `workflow_name` (str): The name of the workflow to display information for

## WorkflowBuilder

Builder class for creating agent workflows.

### Constructor

```python
WorkflowBuilder(name: str)
```

**Parameters:**
- `name` (str): The name for the workflow

### Methods

#### set_description

```python
set_description(description: str) -> WorkflowBuilder
```

Set the workflow description.

**Parameters:**
- `description` (str): The description for the workflow

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### add_llm_agent

```python
add_llm_agent(name: str, model: str, instruction: str, description: Optional[str] = None, tools: Optional[List[str]] = None, output_key: Optional[str] = None, include_contents: str = "default", temperature: float = 0.7, max_output_tokens: int = 1024) -> WorkflowBuilder
```

Add an LLM agent to the workflow.

**Parameters:**
- `name` (str): Unique name for the agent
- `model` (str): Gemini model to use
- `instruction` (str): System instruction for the agent
- `description` (Optional[str]): Description of the agent's purpose
- `tools` (Optional[List[str]]): List of tool names to register with the agent
- `output_key` (Optional[str]): Key to store agent output in session state
- `include_contents` (str): Content inclusion strategy
- `temperature` (float): Temperature for generation
- `max_output_tokens` (int): Maximum output tokens

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### add_sequential_agent

```python
add_sequential_agent(name: str, sub_agents: List[Union[str, dict]], description: Optional[str] = None, max_iterations: int = 5) -> WorkflowBuilder
```

Add a sequential agent to the workflow.

**Parameters:**
- `name` (str): Unique name for the agent
- `sub_agents` (List[Union[str, dict]]): List of sub-agent names or configurations
- `description` (Optional[str]): Description of the agent's purpose
- `max_iterations` (int): Maximum number of iterations (for loop agents)

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### add_parallel_agent

```python
add_parallel_agent(name: str, sub_agents: List[Union[str, dict]], description: Optional[str] = None) -> WorkflowBuilder
```

Add a parallel agent to the workflow.

**Parameters:**
- `name` (str): Unique name for the agent
- `sub_agents` (List[Union[str, dict]]): List of sub-agent names or configurations
- `description` (Optional[str]): Description of the agent's purpose

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### add_loop_agent

```python
add_loop_agent(name: str, sub_agents: List[Union[str, dict]], description: Optional[str] = None, max_iterations: int = 5) -> WorkflowBuilder
```

Add a loop agent to the workflow.

**Parameters:**
- `name` (str): Unique name for the agent
- `sub_agents` (List[Union[str, dict]]): List of sub-agent names or configurations
- `description` (Optional[str]): Description of the agent's purpose
- `max_iterations` (int): Maximum number of iterations

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### set_entry_point

```python
set_entry_point(agent_name: str) -> WorkflowBuilder
```

Set the entry point agent for the workflow.

**Parameters:**
- `agent_name` (str): Name of the entry point agent

**Returns:**
- `WorkflowBuilder`: The builder instance for chaining

#### build

```python
build() -> WorkflowConfig
```

Build and return the workflow configuration.

**Returns:**
- `WorkflowConfig`: The built workflow configuration

**Raises:**
- `ValueError`: If no entry point is set or the entry point agent is not found

## AgentFactory

Factory for creating agents based on configuration.

### Constructor

```python
AgentFactory()
```

### Methods

#### register_tool

```python
register_tool(name: str, tool_func: callable) -> None
```

Register a tool function with a name.

**Parameters:**
- `name` (str): The name to register the tool under
- `tool_func` (callable): The function to register as a tool

#### register_agent

```python
register_agent(name: str, agent) -> None
```

Register a pre-created agent.

**Parameters:**
- `name` (str): The name to register the agent under
- `agent`: The agent instance to register

#### create_agent

```python
create_agent(config: AgentConfig) -> BaseAgent
```

Create an agent based on the provided configuration.

**Parameters:**
- `config` (AgentConfig): The configuration for the agent

**Returns:**
- `BaseAgent`: The created agent

**Raises:**
- `ValueError`: If the agent type is unsupported or tools are not found

## TerminalUIManager


Enhanced UI manager for handling terminal output using the rich library with emojis, animations, and visual effects.

### Constructor

```python
TerminalUIManager(theme: str = "default")
```

**Parameters:**
- `theme` (str): The color theme to use (default, ocean, sunset)

### Methods

#### print_header

```python
print_header(title: str, style: str = None, emoji: str = "🤖") -> None
```

Print a header panel with emoji and enhanced styling.

**Parameters:**
- `title` (str): The title to display
- `style` (str): The style to use for the header (defaults to theme-based color)
- `emoji` (str): Emoji to display in the header

#### print_workflow_info

```python
print_workflow_info(workflow_name: str, description: str = "", agents: List[str] = [], emoji: str = "🔄") -> None
```

Print enhanced workflow information with emojis and better formatting.

**Parameters:**
- `workflow_name` (str): The name of the workflow
- `description` (str): The workflow description
- `agents` (List[str]): List of agent names in the workflow
- `emoji` (str): Emoji to display in the workflow info panel

#### print_running_workflow

```python
print_running_workflow(workflow_name: str, user_id: str, session_id: str, emoji: str = "⚡") -> None
```

Print enhanced information about running workflow with animation and emoji.

**Parameters:**
- `workflow_name` (str): The name of the workflow
- `user_id` (str): The user ID
- `session_id` (str): The session ID
- `emoji` (str): Emoji to display in the running workflow panel

#### print_input

```python
print_input(input_text: str, emoji: str = "💬") -> None
```

Print input text with emoji.

**Parameters:**
- `input_text` (str): The input text to display
- `emoji` (str): Emoji to display with the input

#### print_event

```python
print_event(event: Dict[str, Any], emoji_agent: str = "🤖", emoji_tool: str = "🔧") -> None
```

Print an enhanced event with emojis.

**Parameters:**
- `event` (Dict[str, Any]): The event to display
- `emoji_agent` (str): Emoji to display for agent events
- `emoji_tool` (str): Emoji to display for tool events

#### print_final_output

```python
print_final_output(output: str, emoji: str = "✅") -> None
```

Print enhanced final output with emoji and panel styling.

**Parameters:**
- `output` (str): The final output to display
- `emoji` (str): Emoji to display with the final output

#### print_session_info

```python
print_session_info(session_id: str, user_id: str, emoji_user: str = "👤", emoji_session: str = "🔐") -> None
```

Print enhanced session information with emojis.

**Parameters:**
- `session_id` (str): The session ID
- `user_id` (str): The user ID
- `emoji_user` (str): Emoji to display for user info
- `emoji_session` (str): Emoji to display for session info

#### print_session_state

```python
print_session_state(state: Dict[str, Any], emoji: str = "💾") -> None
```

Print enhanced session state with emoji and better formatting.

**Parameters:**
- `state` (Dict[str, Any]): The session state to display
- `emoji` (str): Emoji to display in the session state panel

#### print_error

```python
print_error(error: str, emoji: str = "❌") -> None
```

Print an enhanced error message with emoji.

**Parameters:**
- `error` (str): The error message to display
- `emoji` (str): Emoji to display with the error

#### print_warning

```python
print_warning(warning: str, emoji: str = "⚠️") -> None
```

Print an enhanced warning message with emoji.

**Parameters:**
- `warning` (str): The warning message to display
- `emoji` (str): Emoji to display with the warning

#### print_info

```python
print_info(info: str, emoji: str = "ℹ️") -> None
```

Print an enhanced info message with emoji.

**Parameters:**
- `info` (str): The info message to display
- `emoji` (str): Emoji to display with the info

#### print_session_creation

```python
print_session_creation(action: str, session_id: Optional[str], emoji_create: str = "✨", emoji_retrieve: str = "🔍") -> None
```

Print enhanced session creation information with emoji.

**Parameters:**
- `action` (str): The action performed
- `session_id` (Optional[str]): The session ID
- `emoji_create` (str): Emoji to display for session creation
- `emoji_retrieve` (str): Emoji to display for session retrieval

#### print_separator

```python
print_separator(char: str = "─", length: int = 60, style: str = "dim") -> None
```

Print an enhanced separator line.

**Parameters:**
- `char` (str): Character to use for the separator
- `length` (int): Length of the separator line
- `style` (str): Style to use for the separator

## Configuration Classes

### AgentType

Enumeration of supported agent types.

```python
class AgentType(Enum):
    LLM = "llm"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"
    CUSTOM = "custom"
```

### BaseAgentConfig

Base configuration for all agents.

```python
class BaseAgentConfig(BaseModel):
    name: str
    description: Optional[str] = None
    type: AgentType
```

### LlmAgentConfig

Configuration for LLM agents.

```python
class LlmAgentConfig(BaseAgentConfig):
    model: str
    instruction: str
    tools: List[str] = []
    output_key: Optional[str] = None
    include_contents: str = "default"
    temperature: float = 0.7
    max_output_tokens: int = 1024
```

### SequentialAgentConfig

Configuration for sequential agents.

```python
class SequentialAgentConfig(BaseAgentConfig):
    sub_agents: List[Union[str, dict]]
    type: AgentType = AgentType.SEQUENTIAL
```

### ParallelAgentConfig

Configuration for parallel agents.

```python
class ParallelAgentConfig(BaseAgentConfig):
    sub_agents: List[Union[str, dict]]
    type: AgentType = AgentType.PARALLEL
```

### LoopAgentConfig

Configuration for loop agents.

```python
class LoopAgentConfig(BaseAgentConfig):
    sub_agents: List[Union[str, dict]]
    max_iterations: int = 5
    type: AgentType = AgentType.LOOP
```

### WorkflowConfig

Configuration for a complete workflow.

```python
class WorkflowConfig(BaseModel):
    name: str
    description: Optional[str] = None
    agents: List[AgentConfig]
    entry_point: str
```