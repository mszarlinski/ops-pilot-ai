# OpsPilot AI — Learning Roadmap

This document tracks the lab series used to build OpsPilot AI incrementally.
Each lab builds on the previous ones. See `CLAUDE.md` for the collaboration
rules that govern how each lab step is worked through.

Status legend: ⬜ not started · 🟨 in progress · ✅ complete

## Lab 01 — Direct LLM Integration

**Objective:** Learn the fundamentals of integrating an LLM into a backend
service: REST API design for AI features, structured outputs, prompt
engineering basics, model invocation, and error handling.

- ✅ **Step 1 — Project bootstrap & deterministic classifier.**
  FastAPI app with `POST /incidents/analyze`. Request/response models defined.
  Classification logic intentionally unimplemented (HTTP 501).
  *Exercise:* implement a deterministic (non-LLM) classifier:
  - Description containing "timeout" (case-insensitive) → `category=STORAGE`,
    `severity=HIGH`.
  - Otherwise → `category=OTHER`, `severity=LOW`.
  - `summary` and `suggested_action` must be non-empty.
  - Invalid input (description outside 10–2000 chars) → HTTP 422.
- ✅ **Step 2 — Replace the deterministic rule with a real LLM call** via the
  Claude API (`client.messages.parse`, structured outputs with
  `output_format=IncidentAnalysis`) instead of free-text parsing.
- ✅ **Step 3 — Error handling & reliability**: `app/llm.py` maps specific
  `anthropic` exceptions to typed `LLMUnavailableError` (transient — rate
  limit, connection error, 5xx) vs `LLMRequestError` (non-retryable — bad
  request, auth), raised with `from err` to preserve the cause. The FastAPI
  endpoint translates these to HTTP 503 and 502 respectively.
- ✅ **Step 4 — Prompt engineering & evaluation**: `category`/`severity`
  constrained to `Literal[...]` enums (5 categories, 3 severities) instead of
  free-form `str`; `SYSTEM_PROMPT` explicitly defines what each category and
  severity means. `tests/test_classification_eval.py` is a fixed, hand-labeled
  13-case eval (opt-in via `RUN_EVALS=1`, since it hits the real API) that
  measures classification accuracy — went from 0% (no value constraints) to
  100% after the schema + prompt changes. Two eval failures along the way
  turned out to be mislabeled ground truth, not model errors — a reminder
  that the eval set itself needs review, not just the prompt.

**Lab 01 complete.**

## Lab 02 — Retrieval-Augmented Generation (RAG)

**Objective:** Document ingestion, chunking, embeddings, vector similarity
search (ChromaDB), full-text search (SQLite FTS), hybrid search, reranking,
and retrieval evaluation. Includes hands-on comparison of semantic vs.
keyword-based retrieval.

- ⬜ **Step 1 — Document ingestion & chunking.** Build a small corpus of
  simulated runbook/KB documents, split them into chunks with metadata
  (source, position), and persist them (SQLite). No search yet — this
  establishes the corpus every later step retrieves from.
- ⬜ **Step 2 — Full-text (keyword) search.** SQLite FTS5 over the chunk
  corpus. This is the traditional-retrieval baseline you'll compare semantic
  search against in Step 4.
- ⬜ **Step 3 — Semantic search.** Embed the chunks and query them via
  ChromaDB (vector similarity). Run the same queries through both FTS and
  vector search side by side to see where each wins and loses.
- ⬜ **Step 4 — Hybrid search, reranking & retrieval evaluation.** Combine
  FTS + vector results, add a reranking step, and build a fixed eval set
  (e.g. precision/recall@k) to measure retrieval quality — reusing the
  evaluation pattern from Lab 01 Step 4, applied to retrieval instead of
  classification.

## Lab 03 — Tool / Function Calling

**Objective:** Expose simulated infrastructure APIs (e.g. "restart service",
"check disk usage") to the LLM as callable tools/functions.

- ⬜ Not started.

## Lab 04 — Model Context Protocol (MCP)

**Objective:** Build an MCP server exposing OpsPilot's tools and connect it
to an MCP-compatible client.

- ⬜ Not started.

## Lab 05 — Workflow Orchestration

**Objective:** Prompt chaining, routing, parallel execution, and
deterministic multi-step workflows without a heavyweight agent framework.

- ⬜ Not started.

## Lab 06 — Event-Driven AI

**Objective:** Asynchronous LLM processing via Redis + RQ, retry strategies,
idempotency, and event-driven integration patterns.

- ⬜ Not started.

## Lab 07 — Human-in-the-Loop

**Objective:** Approval workflows, authorization checks, audit logging, and
safe execution of sensitive remediation actions.

- ⬜ Not started.

## Lab 08 — Agentic Workflows

**Objective:** Autonomous tool selection, multi-step reasoning, execution
limits (max steps/cost/time), and agent state management.

- ⬜ Not started.

## Lab 09 — AI Gateway, Observability & Evaluations

**Objective:** Model routing, cost tracking, tracing/execution logs,
automated evaluation pipelines, and reliability engineering for AI features.

- ⬜ Not started.

## Lab 10 — Agent-to-Agent Communication (optional)

**Objective:** Cooperation between independently deployed AI agents using the
A2A protocol.

- ⬜ Not started.
