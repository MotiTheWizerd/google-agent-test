# ADK Quick Reference Index

> One-glance map of the docs you uploaded. Each item links to the source doc inside your bundle.


## adk-artifacts

- **ADK Artifacts Starter** — A tiny, self-contained starter for working with **Artifacts** in Google's **Agent Development Kit (ADK)**.  
  _Doc:_ `adk-artifacts/README.md`
- **Artifacts — Developer Guide (ADK)** — > Pragmatic notes for using **artifacts** with agents, tools, and callbacks.  
  _Doc:_ `adk-artifacts/Artifacts_Developer_Guide.md`

## adk-bidi-streaming-

- **Google ADK — Bidi‑Streaming Developer Guide (Python)** — This mini‑project shows how to build **bidirectional streaming** (voice/video/text in - streamed agent events out) using the Google **Agent Development Kit (ADK)**, with both **SSE** and **WebSockets** server patterns...  
  _Doc:_ `adk-bidi-streaming-/README.md`

## adk-plugins

- **ADK Plugins — Developer Guide + Examples** — **Target**: Google Agent Development Kit (ADK) - Plugins  
  _Doc:_ `adk-plugins/README.md`

## adk-runtime

- **ADK Runtime Starter — *Running Agents*** — A tiny, working project that shows **how to run ADK agents** using the **Runtime** (event loop + Runner)  
  _Doc:_ `adk-runtime/README.md`
- **Events & Streaming** — Running an agent produces a **stream of `Event`s**. In Python, iterate `async for event in runner.run_async(...)` and render progressively. Detect completion with `event.is_final_response()`. citeturn6view0  
  _Doc:_ `adk-runtime/03_events_and_streaming.md`
- **RunConfig — Runtime Configuration** — Use `RunConfig` to control streaming, speech, modalities, artifact saving, and limits on LLM calls. By default, **no streaming** and inputs aren’t saved as artifacts. citeturn2view0  
  _Doc:_ `adk-runtime/02_runconfig.md`
- **Runtime Overview (ADK)** — The **ADK Runtime** is the engine that orchestrates your agents, tools, and callbacks via an **event loop**.  
  _Doc:_ `adk-runtime/01_runtime_overview.md`
- **Sessions & State (quick)** — - Use `InMemorySessionService` for local dev, or `VertexAiSessionService` for cloud‑backed sessions. citeturn5view0turn4search1  
  _Doc:_ `adk-runtime/04_sessions_and_state.md`
- **Sources** — This mini‑project was written against the official ADK docs and API refs:  
  _Doc:_ `adk-runtime/SOURCES.md`

## adk-streaming

- **ADK Streaming Developer Docs (Mini Project)** — Practical, copy‑pasteable notes for building **bidirectional streaming** with Google's Agent Development Kit (ADK).  
  _Doc:_ `adk-streaming/README.md`
- **ADK Streaming Developer Docs (Mini Project)** — Practical, copy‑pasteable notes for building **bidirectional streaming** with Google's Agent Development Kit (ADK).  
  _Doc:_ `adk-streaming/docs/README.md`
- **Streaming with ADK — Developer Guide** — ADK exposes a **live**, bidirectional loop:  
  _Doc:_ `adk-streaming/streaming.md`
- **Streaming with ADK — Developer Guide** — ADK exposes a **live**, bidirectional loop:  
  _Doc:_ `adk-streaming/docs/streaming.md`

## adk-tools-guide

- **Google ADK — Tools (Developer Guide + Examples)** — This project is a **tools-first** starter for Google’s Agent Development Kit (ADK). It contains:  
  _Doc:_ `adk-tools-guide/README.md`
- **Tools in Google ADK — Practical Guide** — **What is a tool?** A structured, callable action exposed to the LLM: a function with typed params and a docstring that becomes the description. Return JSON‑like dicts with stable keys.  
  _Doc:_ `adk-tools-guide/docs/TOOLS_GUIDE.md`

## agents

- **Google ADK — Agents (Python)** — A compact, implementation‑ready guide to building **agents** with Google’s Agent Development Kit (ADK), with runnable Python examples. Written so an AI agent (or a human) can follow it step‑by‑step.  
  _Doc:_ `agents/agents.md`

## context

- **ADK Developer Guide — **Context**** — > Target: engineers building agents with Google’s Agent Development Kit (ADK). This guide distills how **context** works and how to use it in tools, callbacks, and agents - with copy‑pasteable examples.  
  _Doc:_ `context/context.md`

## events

- **ADK Developer Guide — Events** — A practical, code-first guide to **Events** in Google’s Agent Development Kit (ADK). Use this when wiring UIs, tools, and agents so your app reacts correctly to everything that happens in a conversation.  
  _Doc:_ `events/events.md`

## grounding

- **ADK Grounding Developer Guide (Google Search + Vertex AI Search)** — > Build agents that **cite real sources**. This guide shows how to wire up **Google Search Grounding** and **Vertex AI Search Grounding** in ADK, parse grounding metadata, and render citations with clean Python patterns.  
  _Doc:_ `grounding/grounding.md`

## mcp

- **ADK + MCP Starter (Python)** — This mini project shows how to use **Google Agent Development Kit (ADK)** with the **Model Context Protocol (MCP)** in two patterns:  
  _Doc:_ `mcp/README.md`

## runners

- **ADK Runners — Developer Guide (Python & Java)** — This guide explains how to **run agents with ADK Runners** in Python and Java, how events flow, which services are required, and how to stream results in production. It’s written for building UI backends or headless w...  
  _Doc:_ `runners/runners.md`

## sessions_and_memory

- **ADK Developer Guide — Sessions & Memory (Python)** — This is a practical, code‑first guide for **Sessions** (short‑term, per‑conversation context) and **Memory** (cross‑session, long‑term knowledge) using Google’s Agent Development Kit (ADK).  
  _Doc:_ `sessions_and_memory/sessions_and_memory.md`