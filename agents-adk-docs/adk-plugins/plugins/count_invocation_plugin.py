from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

class CountInvocationPlugin(BasePlugin):
    """Counts agent and model invocations (demo)."""
    def __init__(self) -> None:
        super().__init__(name="count_invocation")
        self.agent_count = 0
        self.llm_request_count = 0

    async def before_agent_callback(self, *, agent: BaseAgent, callback_context: CallbackContext):
        self.agent_count += 1
        print(f"[Plugin/count] agent_runs={self.agent_count}")

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest):
        self.llm_request_count += 1
        print(f"[Plugin/count] llm_requests={self.llm_request_count}")
