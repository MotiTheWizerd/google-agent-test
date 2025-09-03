"""Configuration for the memory module."""
from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

@dataclass(frozen=True)
class Mem0Config:
    api_key: str
    org_id: str | None = None
    project_id: str | None = None
    timeout_s: float = 15.0

    @staticmethod
    def from_env() -> "Mem0Config":
        return Mem0Config(
            api_key=os.getenv("MEM0_API_KEY", "") or "",
            org_id=os.getenv("MEM0_ORG_ID"),
            project_id=os.getenv("MEM0_PROJECT_ID"),
            timeout_s=float(os.getenv("MEM0_TIMEOUT_S", "15.0")),
        )