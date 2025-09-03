"""Interactive Q&A agent that allows users to have a conversation with an AI agent."""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

# Add src to Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.core.agents_manager import AgentsManager


# Load environment variables
load_dotenv()

console = Console()


def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': This is a mock search result. In a real implementation, this would contain actual information about {query}."


async def create_qa_agent():
    """Create a Q&A agent for interactive conversation."""
    # Create agents manager
    manager = AgentsManager(app_name="interactive_qa_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create Q&A workflow
    builder = manager.create_workflow_builder("qa_agent")
    builder.set_description("Interactive Q&A agent that can answer questions and have conversations")
    
    # Add a Q&A agent
    builder.add_llm_agent(
        name="qa_agent",
        model="gemini-2.0-flash",
        instruction="""You are a helpful Q&A assistant. Your role is to engage in natural conversation with users and answer their questions.
Key guidelines:
1. Be friendly, helpful, and conversational
2. If you don't know something, be honest about it
3. You can use the web_search tool to find information when needed
4. Keep your responses concise but informative
5. Ask follow-up questions when appropriate to better understand user needs
6. Maintain context from previous messages in the conversation""",
        tools=["web_search"],
        output_key="qa_response"
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("qa_agent").build()
    manager.register_workflow(workflow)
    
    return manager


async def interactive_conversation():
    """Run an interactive conversation with the Q&A agent."""
    console.print(Panel("🤖 Interactive Q&A Agent", style="bold blue"))
    console.print("Welcome to the interactive Q&A agent!")
    console.print("You can ask questions, have a conversation, or type 'quit' to exit.")
    console.print("")
    
    # Use default user ID
    user_id = "default_user"
    
    # Create the agent
    manager = await create_qa_agent()
    
    console.print(f"[bold green]User ID:[/bold green] {user_id}")
    console.print("[bold green]Session ID:[/bold green] Will be automatically generated")
    console.print("")
    
    # Start the conversation
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold green]You[/bold green]")
            
            # Check if user wants to quit
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break
            
            # Run the workflow (session_id will be automatically generated)
            result = await manager.run_workflow(
                workflow_name="qa_agent",
                input_text=user_input,
                user_id=user_id
            )
            
            # The output is already printed by the manager, but we can add a separator
            console.print("")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(interactive_conversation())