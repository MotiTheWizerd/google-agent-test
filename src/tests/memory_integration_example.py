"""Integration example showing how to use memory with agents."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modules.core.agents_manager import AgentsManager
from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config


# Initialize memory store
try:
    mem_store = Mem0Store(Mem0Config.from_env())
    print("SUCCESS: Memory store initialized")
except Exception as e:
    print(f"ERROR: Failed to initialize memory store: {e}")
    mem_store = None


def web_search(query: str) -> str:
    """Mock web search tool."""
    return f"Search results for '{query}': Latest information about {query} as of 2025."


async def memory_enhanced_agent_example():
    """Example of an agent with memory capabilities."""
    print("=== Memory-Enhanced Agent Example ===\n")
    
    # Create agents manager
    manager = AgentsManager(app_name="memory_enhanced_app")
    
    # Register tools
    manager.register_tool("web_search", web_search)
    
    # Create a research workflow
    builder = manager.create_workflow_builder("memory_research_assistant")
    builder.add_llm_agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="""You are a research assistant that explains topics in detail. 
        When asked about a topic, provide a comprehensive explanation with examples.
        Use the web_search tool when you need current information.
        Structure your response with clear sections and explanations.""",
        tools=["web_search"]
    )
    
    # Build and register workflow
    workflow = builder.set_entry_point("researcher").build()
    manager.register_workflow(workflow)
    
    # Print workflow info
    manager.print_workflow_info("memory_research_assistant")
    
    # Example interaction with memory
    user_id = "researcher_001"
    
    # Store a user preference in memory
    if mem_store:
        try:
            mem_store.add(
                user_id=user_id,
                text="User prefers technical explanations with code examples",
                tags=["preference", "communication_style"],
                source="user_profile"
            )
            print("SUCCESS: Stored user preference in memory")
            
            # Recall user preferences
            preferences = mem_store.search(
                user_id=user_id,
                query="user communication preference",
                k=5
            )
            
            if preferences:
                print(f"SUCCESS: Recalled user preference: {preferences[0]['record']['text']}")
        except Exception as e:
            print(f"ERROR: Error working with memory: {e}")
    
    print("\n" + "="*60)
    print("Research Assistant with Memory Context")
    print("="*60)
    
    # Example question
    print("\nQUESTION: Explain machine learning in simple terms\n")
    
    try:
        result = await manager.run_workflow(
            workflow_name="memory_research_assistant",
            input_text="Explain machine learning in simple terms",
            user_id=user_id,
            session_id="session_001"
        )
        print("\nSUCCESS: Workflow completed successfully!")
        
        # Store the result in memory as well
        if mem_store:
            try:
                mem_store.add(
                    user_id=user_id,
                    text=result["final_output"],
                    tags=["research_result", "ml_explanation"],
                    source="agent_output"
                )
                print("SUCCESS: Stored research result in memory")
            except Exception as e:
                print(f"ERROR: Error storing result in memory: {e}")
                
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n" + "="*60)
    print("SUCCESS: Memory-Enhanced Example Completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(memory_enhanced_agent_example())