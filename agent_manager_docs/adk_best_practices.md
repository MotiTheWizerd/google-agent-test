# Google ADK — Best Practices (Concise)

This is a fast, tactical guide to build reliable, grounded agents with Google’s Agent Development Kit (ADK). It focuses on **what works in production** and skips folder layout.

## 1) Agents: keep roles sharp, prompts small
- Define a **single responsibility** per agent (retrieval, planning, tools, UI streaming).
- Keep system prompts short, **1–3 crisp rules** + capabilities list. Avoid prose.
- Prefer **structured outputs** (JSON-like dicts with fixed keys) for downstream code.

```py
# Example: stable JSON-like tool return
return {
  "action": "create_ticket",
  "status": "success",
  "ticket_id": ticket_id,
  "notes": notes[:500]
}
```

## 2) Tools: contract-first, idempotent, observable
- Treat tools like public APIs: **typed args**, **clear errors**, **deterministic output**.
- **Idempotency**: repeated calls same inputs -> same effect (or safe upserts).
- Include **trace fields** (tool_name, version, timing) in results for logs.
- Validate inputs at the boundary; never pass raw user text to privileged actions.

```py
def tool_send_email(to: str, subject: str, body: str) -> dict:
    assert isinstance(to, str) and "@" in to
    # ... do work
    return {"ok": True, "tool": "send_email", "t_ms": 84, "id": msg_id}
```

## 3) Events: drive your UI and state machine
- Subscribe to **message, tool-call, observation, error** events.
- Use events to update the UI progressively (tokens, partial results, artifacts ready).
- Persist **conversation_id, turn_id, event_id** for replay/debug.

## 4) Sessions & Memory: separate transient vs durable
- **Session state**: ephemeral (cursor, last tool result, in-flight stream).
- **Memory**: durable (facts, preferences, recent summaries). Store as **small, typed items** with TTL when possible.
- Summarize long threads into **compact recaps** every N turns ("what we decided + why").

## 5) Streaming: prefer bidirectional for interactivity
- Use **WS or SSE** for low latency token streams and real-time tool feedback.
- **Backpressure**: buffer and debounce UI updates (e.g., every 50–100 tokens).
- When streaming audio or video, chunk with monotonic timestamps; tolerate packet loss.

## 6) Grounding & citations: never hallucinate where truth matters
- For search or RAG, **attach citations** and show them in the UI.
- Parse grounding metadata and **render source + snippet**; train users to verify.
- Cache retrieval results per turn to reduce cost and drift.

## 7) Artifacts: treat as first-class outputs
- Use artifacts for files (images, code blocks, CSVs). Return **mime type, size, name**.
- Store artifact **hash (SHA-256)** so you can dedupe and verify integrity.
- Stream large artifacts by reference (URL or handle), not inline blobs.

## 8) Runners: make execution boring
- Use runners to **start/stop/observe** long tasks with retries and timeout policy.
- On failure: retry with **exponential backoff**; log final error with a short root-cause field.
- Emit checkpoints so the agent can **resume** without redoing work.

## 9) Plugins & MCP: extend safely
- For third-party capabilities, prefer **MCP servers** with explicit resource scopes.
- Document **rate limits and quotas** per plugin. Enforce client-side throttling.
- Wrap unsafe actions behind a **review state** (human-in-the-loop) if needed.

## 10) Observability: logs > vibes
- Centralize **events, tool calls, inputs/outputs, timings, token usage**.
- Tag every turn with **user_id, session_id, agent_id, version**.
- Capture **minified prompts** (no secrets) for reproducibility.
- Add **redaction** for PII in logs; use reversible encryption only when justified.

## 11) Error strategy: fail loud, recover fast
- Classify errors: _user-input_, _tool_, _network_, _policy_. Handle each explicitly.
- Return machine-usable error envelopes:
```json
{"ok": false, "kind": "tool", "code": "RATE_LIMIT", "retry_in_ms": 800, "msg": "try later"}
```
- If a tool fails repeatedly, **fall back** to a safe summary + suggested next step.

## 12) Cost & latency control
- Use **small models** for routing/extraction; **large models** for reasoning only when needed.
- Cache embeddings and retrieval; **dedupe prompts** across turns.
- Stream early tokens to the UI; **don't block** on long tools if you can show progress.

## 13) Security & policy
- Enforce **allow-lists** for domains/APIs; block direct shell unless explicitly permitted.
- Validate file types; scan uploads; strip active content (macros) by default.
- Respect user consent on data retention; provide a clear **"forget this"** path.

---

### Tiny checklist (printable)
- [ ] Tools have schemas, idempotency, and logs  
- [ ] Events power UI; every turn is replayable  
- [ ] Sessions != Memory; periodic recaps exist  
- [ ] Streaming uses WS/SSE with backpressure  
- [ ] Grounding includes citations & snippets  
- [ ] Artifacts are hashed and deduped  
- [ ] Runners checkpoint and resume  
- [ ] MCP/plugins are scoped and throttled  
- [ ] Errors are typed; retries/backoff in place  
- [ ] Prompts are short; outputs structured  
- [ ] Cost controls & caching in place  
- [ ] PII redaction and consent respected