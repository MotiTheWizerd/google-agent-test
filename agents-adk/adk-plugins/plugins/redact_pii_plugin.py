from google.adk.plugins.base_plugin import BasePlugin
from typing import Optional, Any
import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?:\+?\d[\s-]?)?(?:\(\d{2,3}\)[\s-]?)?\d{3}[\s-]?\d{3,4}")

class RedactPIIPlugin(BasePlugin):
    """Redacts emails/phones in streamed text events."""
    def __init__(self) -> None:
        super().__init__(name="redact_pii")

    def _redact_text(self, text: str) -> str:
        text = _EMAIL.sub("[email‑redacted]", text)
        text = _PHONE.sub("[phone‑redacted]", text)
        return text

    async def on_event_callback(self, *, invocation_context: Any, event: Any) -> Optional[Any]:
        try:
            content = getattr(event, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    if hasattr(part, "text") and isinstance(part.text, str):
                        part.text = self._redact_text(part.text)
            return event
        except Exception:
            return None
