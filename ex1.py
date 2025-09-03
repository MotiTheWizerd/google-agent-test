import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.core.agents_manager import AgentsManager

# Load environment variables
load_dotenv()

async def chat_with_agent():
    """Create a single agent that chats with the user about a subject."""
    
    # Get subject input from user
    subject = input("Enter a subject to discuss: ")
    
    # Create agents manager with app name
    manager = AgentsManager(app_name="single_agent_chat_app")
    
    # Create workflow using builder
    builder = manager.create_workflow_builder("chat_agent")
    builder.add_llm_agent(
        name="chat_agent",
        model="gemini-2.0-flash",
        instruction=f"You are a helpful AI assistant discussing {subject}. Engage in a natural conversation with the user about this topic. Ask follow-up questions, provide interesting insights, and keep the conversation flowing naturally."
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("chat_agent").build()
    manager.register_workflow(workflow)
    
    print(f"Agent: Hello! Let's discuss {subject}.")
    print("(Type 'exit', 'quit', or 'bye' to end the conversation)")
    
    # Initialize session info
    user_id = "chat_user"
    session_id = None  # Will be created automatically
    
    # Conversation loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAgent: Goodbye! It was great discussing", subject, "with you.")
            break
            
        # Run the workflow with user input
        try:
            result = await manager.run_workflow(
                workflow_name="chat_agent",
                input_text=user_input,
                user_id=user_id,
                session_id=session_id
            )
            
            # Extract and display the agent's response
            final_output = result.get("final_output", "I'm not sure how to respond to that.")
            print(f"\nAgent: {final_output}")
            
            # Update session_id for continuity
            session_id = result.get("session_id", session_id)
            
        except Exception as e:
            print(f"\nAgent: I encountered an error: {str(e)}")
            print("Let's continue our conversation.")

def main():
    """Main function to run the chat agent."""
    try:
        asyncio.run(chat_with_agent())
    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Goodbye!")

if __name__ == "__main__":
    main()