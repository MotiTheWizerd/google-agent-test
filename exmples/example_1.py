import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent as Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Create a creative recipe agent that suggests recipes based on available ingredients
recipe_agent = Agent(
    model="gemini-2.0-flash",
    name="creative_chef",
    description="A creative chef that suggests recipes based on available ingredients",
    instruction=(
        "You are a creative chef with a fun personality. When given a list of ingredients, "
        "suggest a recipe that uses those ingredients. Include:\n"
        "1. A fun name for the dish\n"
        "2. A short, enthusiastic description\n"
        "3. Simple steps to prepare\n"
        "4. Any additional tips or serving suggestions\n"
        "Keep your responses concise but engaging. Add emojis where appropriate to make it fun!"
    ),
)

# Tool to get more detailed cooking tips
def get_cooking_tip(topic: str) -> str:
    """Get a helpful cooking tip for a specific topic."""
    tips = {
        "eggs": " Fresher eggs peel more easily when hard-boiled! 🥚",
        "pasta": " Reserve some pasta water before draining - it's great for adjusting sauce consistency! 🍝",
        "chicken": " Let chicken come to room temperature before cooking for more even cooking! 🐔",
        "vegetables": " Don't overcrowd the pan - vegetables steam instead of sauté when overcrowded! 🥦",
        "baking": " Always preheat your oven for better baking results! 🔥",
        "spices": " Toast whole spices before grinding for more flavor! 🌶️",
        "default": " Mise en place (prepping all ingredients before cooking) is the key to stress-free cooking! 👨‍🍳"
    }
    return tips.get(topic.lower(), tips["default"])

# Enhanced agent with tool
recipe_agent_with_tool = Agent(
    model="gemini-2.0-flash",
    name="creative_chef_plus",
    description="A creative chef that suggests recipes and can provide cooking tips",
    instruction=(
        "You are a creative chef with a fun personality. When given a list of ingredients, "
        "suggest a recipe that uses those ingredients. Include:\n"
        "1. A fun name for the dish\n"
        "2. A short, enthusiastic description\n"
        "3. Simple steps to prepare\n"
        "4. Any additional tips or serving suggestions\n\n"
        "You can also provide cooking tips when asked by calling the get_cooking_tip tool. "
        "Use this tool when the user asks for help with specific ingredients or cooking techniques."
    ),
    tools=[get_cooking_tip],
)

async def run_recipe_agent():
    """Run the recipe agent with a sample query"""
    runner = InMemoryRunner(agent=recipe_agent_with_tool, app_name="recipe_app")
    
    # Create a session
    session = await runner.session_service.create_session(
        app_name="recipe_app",
        user_id="chef_user"
    )
    
    # Sample queries
    queries = [
        "I have chicken, potatoes, and rosemary. What can I make?",
        "Can you give me a tip for cooking pasta perfectly?",
        "I want to make something with eggs and spinach"
    ]
    
    for i, query in enumerate(queries):
        print(f"\n{'='*50}")
        print(f"Query {i+1}: {query}")
        print('='*50)
        
        # Run the agent
        async for event in runner.run_async(
            user_id="chef_user",
            session_id=session.id,
            new_message=types.Content(parts=[types.Part(text=query)], role="user")
        ):
            # Print tool calls
            if hasattr(event, 'get_function_calls'):
                for call in event.get_function_calls() or []:
                    print(f"[Tool Call] {call.name}({call.args})")
            
            # Print tool responses
            if hasattr(event, 'get_function_responses'):
                for response in event.get_function_responses() or []:
                    print(f"[Tool Response] {response.response}")
            
            # Print only the final answer
            if event.is_final_response() and event.content:
                print(event.content.parts[0].text)
        
        print("\n" + "-"*50)

if __name__ == "__main__":
    print("🍳 Welcome to the Creative Chef Agent! 🍳")
    print("Let me help you create delicious recipes from your ingredients...")
    
    asyncio.run(run_recipe_agent())
    
    print("\n🍽️ Thanks for using the Creative Chef Agent! Bon appétit! 🍽️")