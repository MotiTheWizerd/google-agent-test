"""Example agent usage with memory integration."""

import os
from src.modules.memory.adapters.mem0_store import Mem0Store
from src.modules.memory.config import Mem0Config

# Initialize the memory store
mem_store = Mem0Store(Mem0Config.from_env())


def on_user_message(session_user_id: str, text: str) -> None:
    """Handle user messages and store relevant memories."""
    # Heuristics - only store durable preferences/facts
    if "i prefer" in text.lower() or "my name is" in text.lower():
        mem_store.add(user_id=session_user_id, text=text, tags=["preference"], source="chat")


def recall_context(session_user_id: str, query: str, k: int = 5) -> list[str]:
    """Recall context from memory."""
    hits = mem_store.search(user_id=session_user_id, query=query, k=k)
    return [h["record"]["text"] for h in hits]


def build_system_prompt(user_id: str, task: str) -> str:
    """Build a system prompt with relevant context."""
    snips = recall_context(user_id, query=task, k=6)
    context = "\n".join(f"- {s}" for s in snips)
    return f"""You are a helpful agent. Use these user memories when relevant:

{context}

Task: {task}
Only rely on a memory if it is clearly relevant and not contradicted by new info.
"""


# Export for analytics / audits
schema = {
    "title": "MemExport",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "user_id": {"type": "string"},
        "text": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "metadata": {"type": "object"}
    },
    "required": ["id", "user_id", "text"]
}


def export_user_memories(user_id: str) -> dict:
    """Export memories for a specific user."""
    return mem_store.export(
        schema=schema, 
        filters={"AND": [{"user_id": user_id}]}
    )


# Drop-in example (end-to-end)
if __name__ == "__main__":
    # Set API key (in practice, use environment variables)
    os.environ.setdefault("MEM0_API_KEY", "<YOUR_KEY>")
    
    # Initialize store
    store = Mem0Store(Mem0Config.from_env())

    # 1) Store a fact
    store.add(
        user_id="moti", 
        text="I prefer window seats on long flights", 
        tags=["preference", "travel"]
    )

    # 2) Recall before replying
    mems = store.search(user_id="moti", query="flight seat preference", k=5)
    context = "\n".join("- " + m["record"]["text"] for m in mems)
    print("Context for prompt:\n", context)