# RunConfig — Runtime Configuration

Use `RunConfig` to control streaming, speech, modalities, artifact saving, and limits on LLM calls. By default, **no streaming** and inputs aren’t saved as artifacts. citeturn2view0

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,  # NONE | SSE | BIDI
    max_llm_calls=200,
)
```
Key parameters: `speech_config`, `response_modalities`, `save_input_blobs_as_artifacts`, `support_cfc` (experimental, Python), `streaming_mode`, `output_audio_transcription`, `max_llm_calls`. See official table for details. citeturn2view0
