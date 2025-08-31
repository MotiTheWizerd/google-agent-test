import asyncio
from google.adk.agents import LlmAgent

from modules.Agents.agent_manager import AgentManager


def build_manager() -> AgentManager:
    """Construct an ``AgentManager`` with a custom root and sub-agents."""

    greeter = LlmAgent(
        model="gemini-2.0-flash",
        name="Greeter",
        instruction="Greet the user before responding.",
    )

    expert = LlmAgent(
        model="gemini-2.0-flash",
        name="Expert",
        instruction="Answer questions clearly and concisely.",
    )

    coordinator = LlmAgent(
        model="gemini-2.0-flash",
        name="TeamLeader",
        instruction="Coordinate sub-agents and provide the final answer.",
    )

    return AgentManager(root_agent=coordinator, sub_agents=[greeter, expert])


async def chat_with_agent() -> None:
    manager = build_manager()
    session_id = "chat_session_1"
    print("Welcome to the agent chat! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        print("Agent: ", end="", flush=True)
        await manager.run(user_input, session_id)
        print()


if __name__ == "__main__":
    asyncio.run(chat_with_agent())
