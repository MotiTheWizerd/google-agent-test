import asyncio
from modules.Agents.agent_manager import AgentManager

async def chat_with_agent():
    manager = AgentManager()
    session_id = "chat_session_1"
    print("Welcome to the agent chat! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = await manager.run(user_input, session_id)
        print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(chat_with_agent())
