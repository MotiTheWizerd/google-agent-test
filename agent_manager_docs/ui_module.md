# UI Module Documentation

## Overview

The UI Module provides a dedicated UI manager for handling all terminal output using the rich library. This separation of concerns allows for:

1. **Cleaner Code**: Business logic is separated from presentation logic
2. **Easier Maintenance**: UI changes can be made without affecting core functionality
3. **Better Testability**: UI components can be tested independently
4. **Flexibility**: Different UI implementations can be swapped in the future

The `TerminalUIManager` class provides methods for all common UI operations such as printing headers, workflow information, session details, errors, and agent responses.

## Installation

Make sure you have the required dependencies installed using Poetry:

```bash
poetry install
```

The required dependencies are specified in `pyproject.toml` and include `google-adk`, `rich`, `python-dotenv`, `pydantic`, and `mem0ai`.

## Quick Start

```python
from modules.ui.terminal_ui_manager import TerminalUIManager

# Create UI manager instance
ui = TerminalUIManager()

# Use UI methods
ui.print_header("Welcome to Agents Manager")
ui.print_info("System initialized successfully")
```

## TerminalUIManager API

### Constructor

```python
TerminalUIManager()
```

Creates a new instance of the TerminalUIManager with a rich Console instance.

### Methods

#### print_header

```python
print_header(title: str, style: str = "bold blue") -> None
```

Print a header panel with the specified title and style.

**Parameters:**
- `title` (str): The title to display in the header
- `style` (str): The style to use for the header (default: "bold blue")

#### print_workflow_info

```python
print_workflow_info(workflow_name: str, description: str = "", agents: List[str] = []) -> None
```

Print workflow information in a formatted table.

**Parameters:**
- `workflow_name` (str): The name of the workflow
- `description` (str): The workflow description (optional)
- `agents` (List[str]): List of agent names in the workflow (optional)

#### print_running_workflow

```python
print_running_workflow(workflow_name: str, user_id: str, session_id: str) -> None
```

Print information about a running workflow.

**Parameters:**
- `workflow_name` (str): The name of the workflow
- `user_id` (str): The user ID
- `session_id` (str): The session ID

#### print_input

```python
print_input(input_text: str) -> None
```

Print input text with a green label.

**Parameters:**
- `input_text` (str): The input text to display

#### print_event

```python
print_event(event: Dict[str, Any]) -> None
```

Print an event with appropriate formatting based on event type.

**Parameters:**
- `event` (Dict[str, Any]): The event to display

Supported event types:
- `model_response`: Agent responses
- `tool_call`: Tool calls made by agents
- `tool_response`: Responses from tool executions

#### print_final_output

```python
print_final_output(output: str) -> None
```

Print final output with bold green styling.

**Parameters:**
- `output` (str): The final output to display

#### print_session_info

```python
print_session_info(session_id: str, user_id: str) -> None
```

Print session information.

**Parameters:**
- `session_id` (str): The session ID
- `user_id` (str): The user ID

#### print_session_state

```python
print_session_state(state: Dict[str, Any]) -> None
```

Print session state in a formatted table.

**Parameters:**
- `state` (Dict[str, Any]): The session state to display

#### print_error

```python
print_error(error: str) -> None
```

Print an error message with red styling.

**Parameters:**
- `error` (str): The error message to display

#### print_warning

```python
print_warning(warning: str) -> None
```

Print a warning message with yellow styling.

**Parameters:**
- `warning` (str): The warning message to display

#### print_info

```python
print_info(info: str) -> None
```

Print an info message with blue styling.

**Parameters:**
- `info` (str): The info message to display

#### print_session_creation

```python
print_session_creation(action: str, session_id: Optional[str]) -> None
```

Print session creation information.

**Parameters:**
- `action` (str): The action performed
- `session_id` (Optional[str]): The session ID

#### print_separator

```python
print_separator() -> None
```

Print a separator line.

## Usage Examples

### Basic Usage

```python
from modules.ui.terminal_ui_manager import TerminalUIManager

ui = TerminalUIManager()

# Print a header
ui.print_header("Agents Manager System")

# Print workflow information
ui.print_workflow_info(
    workflow_name="research_assistant",
    description="Research assistant that uses web search tools",
    agents=["researcher", "writer", "reviewer"]
)

# Print session info
ui.print_session_info("sess_12345", "user_001")

# Print messages
ui.print_input("What is the weather in Paris?")
ui.print_final_output("The weather in Paris is sunny with a temperature of 22°C.")
```

### Error Handling

```python
try:
    # Some operation that might fail
    result = perform_operation()
except Exception as e:
    ui.print_error(f"Operation failed: {str(e)}")
```

### Session State Display

```python
# Display session state
session_state = {
    "user_preference": "detailed",
    "last_topic": "weather",
    "research_notes": "Weather in Paris is typically mild in spring"
}
ui.print_session_state(session_state)
```

## Best Practices

### 1. Consistent Styling
- Use consistent colors for similar types of information
- Follow the existing color scheme (blue for headers/info, green for success, red for errors, yellow for warnings)

### 2. Appropriate Information Display
- Use `print_header` for main sections
- Use `print_info` for general information
- Use `print_warning` for non-critical issues
- Use `print_error` for actual errors
- Use `print_final_output` for the final result of operations

### 3. Event Handling
- Use `print_event` to display agent events in a structured way
- Format different event types appropriately

### 4. Session Management
- Always display session information when starting operations
- Show session state when it's relevant to the user

### 5. User Experience
- Use separators to visually separate different sections
- Provide clear, concise messages
- Use appropriate panel styles for different types of information

## Visual Examples

### Header Display
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Agents Manager System                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Information Table
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Workflow: research_assistant                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Property      │ Value                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Description   │ Research assistant that uses web search tools                │
│ Agents        │ researcher, writer, reviewer                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Session State Table
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             Session State                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Key           │ Value                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ user_pref     │ detailed                                                     │
│ last_topic    │ weather                                                      │
│ research_notes│ Weather in Paris is typically mild in spring                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Error Message
```
Error: Failed to connect to the database
```

## Integration with AgentsManager

The TerminalUIManager is automatically integrated with the AgentsManager:

```python
from modules.core.agents_manager import AgentsManager

# The UI manager is automatically created
manager = AgentsManager(app_name="my_app")

# UI methods are called internally
result = await manager.run_workflow(
    workflow_name="simple_workflow",
    input_text="Hello, how are you?",
    user_id="user_123"
)
# UI output is automatically displayed during workflow execution
```

## Customization

You can customize the TerminalUIManager by subclassing it:

```python
from modules.ui.terminal_ui_manager import TerminalUIManager

class CustomUIManager(TerminalUIManager):
    def print_custom_header(self, title: str):
        self.console.print(f"=== {title} ===", style="bold magenta")
        
    def print_custom_workflow_info(self, workflow_name: str, description: str = ""):
        self.console.print(f"Workflow: {workflow_name}", style="bold cyan")
        if description:
            self.console.print(f"Description: {description}", style="italic")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the `src` directory is in your Python path
2. **Styling Issues**: Ensure you're using valid rich styling options
3. **Display Problems**: Check that your terminal supports ANSI colors

### Debugging Tips

- Use `print_info` for debugging messages
- Use `print_separator` to visually separate debug sections
- Use `print_session_state` to inspect session state during development