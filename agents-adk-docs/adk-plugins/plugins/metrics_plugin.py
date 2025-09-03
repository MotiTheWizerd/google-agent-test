from google.adk.plugins.base_plugin import BasePlugin
from prometheus_client import Counter, Histogram, start_http_server
import time

class MetricsPlugin(BasePlugin):
    """Exports basic Prometheus metrics for model and tool usage."""
    def __init__(self, port: int = 9100):
        super().__init__(name="metrics")
        start_http_server(port)
        self.model_calls = Counter("adk_model_calls_total", "Total LLM calls")
        self.tool_calls = Counter("adk_tool_calls_total", "Total tool calls")
        self.model_latency = Histogram("adk_model_latency_seconds", "LLM call latency (s)")

    async def before_model_callback(self, *, **kwargs):
        self._start = time.perf_counter()

    async def after_model_callback(self, *, **kwargs):
        self.model_calls.inc()
        if hasattr(self, "_start"):
            self.model_latency.observe(time.perf_counter() - self._start)

    async def after_tool_callback(self, *, **kwargs):
        self.tool_calls.inc()
