# ADK Grounding Developer Guide (Google Search + Vertex AI Search)

> Build agents that **cite real sources**. This guide shows how to wire up **Google Search Grounding** and **Vertex AI Search Grounding** in ADK, parse grounding metadata, and render citations with clean Python patterns.

---

## 1) When to use which grounding
- **Google Search Grounding** — live/public web facts (news, scores, prices). The model performs searches, composes an answer, and returns **groundingMetadata** (chunks + supports) and **search suggestions** you can render.
- **Vertex AI Search Grounding** — enterprise/private data. The model queries your **Vertex AI Search** datastore; answers come grounded in your documents with citations.

**Both** return a structured `groundingMetadata` payload you can mine to display **which source supports which sentence**.

---

## 2) Quickstarts (Python)

### 2.1 Google Search Grounding
```python
from google.adk.agents import Agent
from google.adk.tools import google_search  # Built‑in tool

root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    description="Answers with up-to-date facts and cites sources using Google Search.",
    instruction=(
        "You are an expert researcher. Use Google Search when a query needs fresh or verifiable info. "
        "Always include citations when available."
    ),
    tools=[google_search],
)
```
**Run:**
```bash
# Dev UI
adk web
# or Terminal
adk run google_search_agent
```
**Platform env:**
- Google AI Studio: `.env` → `GOOGLE_GENAI_USE_VERTEXAI=FALSE`, `GOOGLE_API_KEY=...`
- Vertex AI: `.env` → `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GOOGLE_CLOUD_PROJECT=...`, `GOOGLE_CLOUD_LOCATION=...`

### 2.2 Vertex AI Search Grounding
```python
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

DATASTORE_ID = (
    "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/"
    "dataStores/YOUR_DATASTORE_ID"
)

root_agent = Agent(
    name="vertex_search_agent",
    model="gemini-2.5-flash",
    description="Enterprise doc QA grounded on your Vertex AI Search datastore.",
    instruction=(
        "Answer strictly using the most relevant enterprise documents retrieved via Vertex AI Search. "
        "Summarize clearly and include citations when available."
    ),
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)],
)
```
**Auth:** use Vertex AI credentials in `.env` (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`, project + location).

**Run:** `adk web` or `adk run vertex_search_agent`

---

## 3) Event stream patterns (final text + citations)
ADK yields **Events**. For the final agent message, grab `event.content.parts[0].text`. If `event.grounding_metadata` is present, you can map text segments to their sources.

```python
async for event in runner.run_async(agent=root_agent, user="Who won Euro 2024? Cite sources."):
    if event.is_final_response():
        text = event.content.parts[0].text
        print(text)

        gm = getattr(event, "grounding_metadata", None)
        if gm:  # works for both Google Search + Vertex AI Search grounding
            from examples.utils.citations import print_inline_citations
            print_inline_citations(text, gm)
```

### 3.1 Anatomy of `groundingMetadata`
- **groundingChunks** — list of sources (public URLs or enterprise documents). Each has `title` + `uri` (or `document: {title, uri, id}` for Vertex).
- **groundingSupports** — links **segments** of the final text (`startIndex`, `endIndex`, `text`) to `groundingChunkIndices` (ints pointing into `groundingChunks`).
- *(Google Search only)* **searchEntryPoint** — preformatted HTML to render Google-branded search chips.

---

## 4) Rendering citations
Two levels:

**Minimal (terminal):**
- Append footnote markers like `[1]` after supported sentences and dump a sources list.

**Enhanced (UI):**
- Wrap supported spans in clickable chips that reveal `title` and `uri`.
- For Google Search, also inject the provided `searchEntryPoint` HTML in your header.

**Utility (ready to drop):** see `examples/utils/citations.py` — it normalizes both Google Search and Vertex shapes and prints inline markers + footnotes.

---

## 5) Prompts that exercise grounding
- “What did Alphabet report for Google Cloud revenue in **2022 Q1**? Cite sources.”
- “Who won the latest Ballon d’Or? Add sources.”
- “Summarize our internal **AI policy** and cite the exact doc names.” *(Vertex)*

---

## 6) Best practices
- **Be explicit in system instruction**: tell the agent to prefer grounded info and **always cite** when available.
- **Display citations**: users trust answers more when they can click sources.
- **Guardrails**: for private data, check user permissions before surfacing doc links; convert internal URIs to accessible links.
- **Suggestions (Google Search)**: render `searchEntryPoint` chips to encourage follow‑ups.
- **Windows tip**: if `adk web` hits `_make_subprocess_transport NotImplementedError`, run `adk web --no-reload`.

---

## 7) Project skeleton (included here)
```
root/
├─ README.md  — this guide
├─ .env.example
└─ examples/
   ├─ google_search_agent/agent.py
   ├─ vertex_search_agent/agent.py
   └─ utils/citations.py
```

Copy the example agents into your app and run with `adk web` or `adk run ...`.

---

## 8) Troubleshooting
- **No agent in dropdown**: Run `adk web` from the parent folder of your agent package.
- **No citations**: The model may choose not to ground if it’s confident the answer is common knowledge. Nudge via instruction.
- **Vertex 401/permission errors**: Re‑auth (`gcloud auth login`), confirm project/location, and your **Data Store ID** string.

---

## 9) Next
- Add **callbacks** to log grounding usage and render a sidebar of sources.
- Add **Artifacts** to persist the final text + resolved citations for auditing.
