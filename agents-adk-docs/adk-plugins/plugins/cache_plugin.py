from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types
import hashlib, json, time

class CachePlugin(BasePlugin):
    """Simple in-memory LLM response cache using request signature."""
    def __init__(self, ttl_seconds: int | None = None, max_items: int = 4096):
        super().__init__(name="cache")
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._store: dict[str, tuple[float, LlmResponse]] = {}

    def _key_for(self, llm_request: LlmRequest) -> str:
        model = getattr(llm_request.config, "model", "")
        sys = getattr(llm_request.config, "system_instruction", None)
        sys_text = ""
        if isinstance(sys, types.Content) and sys.parts:
            sys_text = "".join([getattr(p, "text", "") for p in sys.parts])
        user = ""
        if llm_request.contents:
            for c in llm_request.contents:
                if c.role == "user":
                    for p in (c.parts or []):
                        user += getattr(p, "text", "")
        blob = json.dumps({"m": model, "sys": sys_text, "u": user}, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest):
        k = self._key_for(llm_request)
        hit = self._store.get(k)
        if not hit:
            return None
        ts, resp = hit
        if self.ttl_seconds is not None and (time.time() - ts) > self.ttl_seconds:
            self._store.pop(k, None)
            return None
        print("[Plugin/cache] HIT — skipping model call")
        return resp

    async def after_model_callback(self, *, callback_context: CallbackContext, llm_response: LlmResponse):
        # Save response under the last request known to context (ADK exposes request in context/state)
        req = getattr(callback_context, "state", {}).get("last_llm_request", None) or getattr(callback_context, "llm_request", None)
        if req:
            k = self._key_for(req)
            if len(self._store) >= self.max_items:
                self._store.pop(next(iter(self._store)))
            self._store[k] = (time.time(), llm_response)
