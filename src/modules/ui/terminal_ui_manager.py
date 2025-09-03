"""Terminal UI Manager for handling rich console output with enhanced visual elements."""

import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
from typing import Any, Dict, List, Optional


class TerminalUIManager:
    """Manages terminal UI output using rich library with enhanced visual elements."""
    
    def __init__(self, theme: str = "default"):
        """Initialize the terminal UI manager."""
        self.console = Console()
        self.theme = theme
        self.themes = {
            "default": {
                "header": "bold #FF6B6B on #2D3748",
                "workflow": "bold #48BB78 on #2D3748",
                "agent": "bold #63B3ED",
                "tool": "bold #F6AD55",
                "success": "bold #48BB78",
                "error": "bold #FC8181",
                "warning": "bold #F6AD55",
                "info": "bold #63B3ED",
                "input": "bold #B794F6",
                "output": "bold #48BB78"
            },
            "ocean": {
                "header": "bold #00CED1 on #001F3F",
                "workflow": "bold #7FFFD4 on #001F3F",
                "agent": "bold #00FFFF",
                "tool": "bold #20B2AA",
                "success": "bold #00FA9A",
                "error": "bold #FF4500",
                "warning": "bold #FFD700",
                "info": "bold #87CEEB",
                "input": "bold #9370DB",
                "output": "bold #00FA9A"
            },
            "sunset": {
                "header": "bold #FF6347 on #2F2F2F",
                "workflow": "bold #FFA500 on #2F2F2F",
                "agent": "bold #FFD700",
                "tool": "bold #FF69B4",
                "success": "bold #32CD32",
                "error": "bold #DC143C",
                "warning": "bold #FF8C00",
                "info": "bold #1E90FF",
                "input": "bold #9932CC",
                "output": "bold #32CD32"
            }
        }
        self.current_theme = self.themes.get(theme, self.themes["default"])
    
    def _get_color(self, element: str) -> str:
        """Get color for an element based on current theme."""
        return self.current_theme.get(element, "white")
    
    def print_header(self, title: str, style: str = None, emoji: str = "🤖") -> None:
        """Print a header panel with emoji."""
        if style is None:
            style = self._get_color("header")
        
        # Create header with emoji
        header_text = f"{emoji} {title} {emoji}"
        self.console.print(Panel(header_text, style=style, expand=True))
    
    def print_workflow_info(self, workflow_name: str, description: str = "", agents: List[str] = [], emoji: str = "🔄") -> None:
        """Print workflow information with emojis and better formatting."""
        # Create a workflow info panel with emoji
        workflow_title = f"{emoji} Workflow: {workflow_name} {emoji}"
        
        # Create table with enhanced styling
        table = Table(
            title=workflow_title,
            show_header=True,
            header_style=f"bold {self._get_color('workflow')}",
            border_style=self._get_color("workflow"),
            expand=True
        )
        table.add_column("Property 📋", style="dim", width=15)
        table.add_column("Value 💎")
        
        if description:
            table.add_row("📝 Description", description)
        
        if agents:
            agents_list = "\n".join([f"🔹 {agent}" for agent in agents])
            table.add_row("🤖 Agents", agents_list)
        else:
            table.add_row("🤖 Agents", "None configured")
        
        self.console.print(table)
    
    def print_running_workflow(self, workflow_name: str, user_id: str, session_id: str, emoji: str = "⚡") -> None:
        """Print information about running workflow with emoji."""
        # Create running workflow panel with emoji
        workflow_text = f"{emoji} Executing Workflow: [bold]{workflow_name}[/bold] {emoji}"
        self.console.print(Panel(workflow_text, style=self._get_color("workflow"), expand=True))
        
        # Show user and session info with emojis
        user_info = f"👤 User: [bold]{user_id}[/bold] | 🔐 Session: [bold]{session_id}[/bold]"
        self.console.print(user_info, style=self._get_color("info"))
        
        # Add a progress spinner for visual feedback
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Initializing workflow...", total=None)
            time.sleep(0.5)
            progress.update(task, description="[green]Workflow started! 🚀")
            time.sleep(0.3)
    
    def print_input(self, input_text: str, emoji: str = "💬") -> None:
        """Print input text with emoji."""
        self.console.print(f"{emoji} [bold {self._get_color('input')}]User Input:[/bold {self._get_color('input')}] {input_text}")
    
    def print_event(self, event: Dict[str, Any], emoji_agent: str = "🤖", emoji_tool: str = "🔧") -> None:
        """Print an event with emojis."""
        event_type = event.get("type", "unknown")
        
        if event_type == "model_response":
            content = event.get("content", {})
            if content and isinstance(content, dict) and "parts" in content:
                parts = content["parts"]
                if parts and isinstance(parts, list) and len(parts) > 0:
                    text = parts[0].get("text", "") if isinstance(parts[0], dict) else str(parts[0])
                    self.console.print(f"{emoji_agent} [bold {self._get_color('agent')}]Agent Response:[/bold {self._get_color('agent')}] {text}")
        elif event_type == "tool_call":
            tool_call = event.get("tool_call", {})
            if tool_call and isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "unknown")
                args = tool_call.get("args", {})
                self.console.print(f"{emoji_tool} [bold {self._get_color('tool')}]Tool Call:[/bold {self._get_color('tool')}] [yellow]{tool_name}[/yellow]({args})")
        elif event_type == "tool_response":
            tool_response = event.get("tool_response", {})
            if tool_response and isinstance(tool_response, dict):
                tool_name = tool_response.get("name", "unknown")
                response = tool_response.get("response", "")
                self.console.print(f"{emoji_tool} [bold {self._get_color('tool')}]Tool Response:[/bold {self._get_color('tool')}] [yellow]{tool_name}[/yellow] ➡️ {response}")
    
    def print_final_output(self, output: str, emoji: str = "✅") -> None:
        """Print final output with emoji."""
        # Create a final output panel with emoji
        self.console.print(Panel(
            f"{emoji} [bold {self._get_color('success')}]Final Output[/bold {self._get_color('success')}]\n\n{output}",
            style=self._get_color("success"),
            expand=True
        ))
    
    def print_session_info(self, session_id: str, user_id: str, emoji_user: str = "👤", emoji_session: str = "🔐") -> None:
        """Print session information with emojis."""
        self.console.print(f"{emoji_user} [bold {self._get_color('info')}]User ID:[/bold {self._get_color('info')}] {user_id}")
        self.console.print(f"{emoji_session} [bold {self._get_color('info')}]Session ID:[/bold {self._get_color('info')}] {session_id}")
    
    def print_session_state(self, state: Dict[str, Any], emoji: str = "💾") -> None:
        """Print session state with emoji."""
        if state:
            # Create a session state panel with emoji
            state_title = f"{emoji} Session State {emoji}"
            
            table = Table(
                title=state_title,
                show_header=True,
                header_style=f"bold {self._get_color('info')}",
                border_style=self._get_color("info"),
                expand=True
            )
            table.add_column("Key 🔑", style="dim", width=20)
            table.add_column("Value 💎")
            
            for key, value in state.items():
                table.add_row(str(key), str(value))
            
            self.console.print(table)
    
    def print_error(self, error: str, emoji: str = "❌") -> None:
        """Print an error message with emoji."""
        error_text = f"{emoji} [bold {self._get_color('error')}]Error:[/bold {self._get_color('error')}] {error}"
        self.console.print(error_text)
    
    def print_warning(self, warning: str, emoji: str = "⚠️") -> None:
        """Print a warning message with emoji."""
        self.console.print(f"{emoji} [bold {self._get_color('warning')}]Warning:[/bold {self._get_color('warning')}] {warning}")
    
    def print_info(self, info: str, emoji: str = "ℹ️") -> None:
        """Print an info message with emoji."""
        self.console.print(f"{emoji} [bold {self._get_color('info')}]Info:[/bold {self._get_color('info')}] {info}")
    
    def print_session_creation(self, action: str, session_id: Optional[str], emoji_create: str = "✨", emoji_retrieve: str = "🔍") -> None:
        """Print session creation information with emoji."""
        emoji = emoji_create if "create" in action.lower() else emoji_retrieve
        session_display = session_id if session_id else 'None'
        self.console.print(f"{emoji} [bold {self._get_color('info')}]{action}:[/bold {self._get_color('info')}] {session_display}")
    
    def print_separator(self, char: str = "─", length: int = 60, style: str = "dim") -> None:
        """Print a separator line."""
        separator = char * length
        self.console.print(separator, style=style)