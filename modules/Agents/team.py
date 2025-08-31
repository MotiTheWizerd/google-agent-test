from __future__ import annotations

from typing import Optional, Sequence

from google.adk.agents import LlmAgent as Agent, BaseAgent


def build_team_root(sub_agents: Optional[Sequence[BaseAgent]] = None) -> BaseAgent:
    """Create a TeamLeader agent coordinating given ``sub_agents``.

    If ``sub_agents`` is ``None`` a default Greeter and Expert pair is used.
    """
    if sub_agents is None:
        greeter = Agent(
            model="gemini-2.0-flash",
            name="Greeter",
            instruction="Greet the user before responding.",
        )

        expert = Agent(
            model="gemini-2.0-flash",
            name="Expert",
            instruction="Answer questions clearly and concisely.",
        )

        sub_agents = [greeter, expert]
    else:
        sub_agents = list(sub_agents)

    return Agent(
        model="gemini-2.0-flash",
        name="TeamLeader",
        instruction="Coordinate sub-agents and provide the final answer.",
        sub_agents=sub_agents,
    )


def configure_root(
    root_agent: Optional[BaseAgent], sub_agents: Optional[Sequence[BaseAgent]]
) -> BaseAgent:
    """Build or augment ``root_agent`` with the provided ``sub_agents``."""
    if root_agent is None:
        return build_team_root(sub_agents)

    if sub_agents:
        if hasattr(root_agent, "sub_agents"):
            existing = list(getattr(root_agent, "sub_agents") or [])
            setattr(root_agent, "sub_agents", existing + list(sub_agents))
        else:
            raise ValueError(
                "sub_agents were provided but the root_agent does not support sub_agents"
            )
    return root_agent
