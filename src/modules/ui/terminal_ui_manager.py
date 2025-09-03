"""Terminal UI Manager for handling rich console output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Any, Dict, List, Optional


class TerminalUIManager:
    """Manages terminal UI output using rich library."""
    
    def __init__(self):
        """Initialize the terminal UI manager."""
        self.console = Console()
    
    def print_header(self, title: str, style: str = "bold blue") -> None:
        """Print a header panel."""
        self.console.print(Panel(title, style=style))
    
    def print_workflow_info(self, workflow_name: str, description: str = "", agents: List[str] = []) -> None:
        """Print workflow information."""
        table = Table(title=f"Workflow: {workflow_name}", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="dim", width=12)
        table.add_column("Value")
        
        if description:
            table.add_row("Description", description)
        
        if agents:
            table.add_row("Agents", ", ".join(agents))
        
        self.console.print(table)
    
    def print_running_workflow(self, workflow_name: str, user_id: str, session_id: str) -> None:
        """Print information about running workflow."""
        self.console.print(Panel(f"Running workflow: {workflow_name}", style="bold blue"))
        self.console.print(f"User: {user_id}, Session: {session_id}")
    
    def print_input(self, input_text: str) -> None:
        """Print input text."""
        self.console.print(f"[green]Input:[/green] {input_text}")
    
    def print_event(self, event: Dict[str, Any]) -> None:
        """Print an event."""
        if event.get("type") == "model_response":
            content = event.get("content", {})
            if content and isinstance(content, dict) and "parts" in content:
                parts = content["parts"]
                if parts and isinstance(parts, list) and len(parts) > 0:
                    text = parts[0].get("text", "") if isinstance(parts[0], dict) else str(parts[0])
                    self.console.print(f"[cyan]Agent Response:[/cyan] {text}")
        elif event.get("type") == "tool_call":
            tool_call = event.get("tool_call", {})
            if tool_call and isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "unknown")
                args = tool_call.get("args", {})
                self.console.print(f"[yellow]Tool Call:[/yellow] {tool_name}({args})")
        elif event.get("type") == "tool_response":
            tool_response = event.get("tool_response", {})
            if tool_response and isinstance(tool_response, dict):
                tool_name = tool_response.get("name", "unknown")
                response = tool_response.get("response", "")
                self.console.print(f"[yellow]Tool Response:[/yellow] {tool_name} -> {response}")
    
    def print_final_output(self, output: str) -> None:
        """Print final output."""
        self.console.print(f"[bold green]Final Output:[/bold green] {output}")
    
    def print_session_info(self, session_id: str, user_id: str) -> None:
        """Print session information."""
        self.console.print(f"[bold green]Session ID:[/bold green] {session_id}")
        self.console.print(f"[bold green]User ID:[/bold green] {user_id}")
    
    def print_session_state(self, state: Dict[str, Any]) -> None:
        """Print session state."""
        if state:
            table = Table(title="Session State", show_header=True, header_style="bold magenta")
            table.add_column("Key", style="dim", width=20)
            table.add_column("Value")
            
            for key, value in state.items():
                table.add_row(key, str(value))
            
            self.console.print(table)
    
    def print_error(self, error: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]Error:[/red] {error}")
    
    def print_warning(self, warning: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]Warning:[/yellow] {warning}")
    
    def print_info(self, info: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]Info:[/blue] {info}")
    
    def print_session_creation(self, action: str, session_id: Optional[str]) -> None:
        """Print session creation information."""
        self.console.print(f"[blue]{action}[/blue]: {session_id if session_id else 'None'}")
    
    def print_separator(self) -> None:
        """Print a separator line."""
        self.console.print("-" * 50)