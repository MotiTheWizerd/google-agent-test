# Sessions & State (quick)
- Use `InMemorySessionService` for local dev, or `VertexAiSessionService` for cloud‑backed sessions. citeturn5view0turn4search1
- Runner appends the user message to the session, processes yielded events, and commits their **state/artifact deltas** through services. citeturn1view0
- By default, the dev UI stores sessions in memory; use a durable service in production. citeturn4search10
