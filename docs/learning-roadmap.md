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

- ✅ **Step 1 — Document ingestion & chunking.** `data/runbooks/*.md` is a
  5-document corpus (storage, object storage, network/VPN, API errors,
  frontend) mirroring the Lab 01 category taxonomy. `app/chunking.py`
  implements fixed-size chunking with overlap via direct string slicing
  (`text[start:start+chunk_size]`, `start` advancing by
  `chunk_size - overlap`) — no manual character accumulation. `app/documents.py`
  persists chunks to SQLite (`chunks` table) via `ingest_documents`.
- ✅ **Step 2 — Full-text (keyword) search.** `app/search.py` creates a
  `chunks_fts` FTS5 virtual table (`id`/`document_id` marked `UNINDEXED`, so a
  query can't match a chunk on its own identifier), rebuilds it from `chunks`
  on each `index_chunks` call for idempotency, and ranks `MATCH` results with
  `bm25()`. The score's sign is flipped on the way out so higher means a
  better match — the convention Step 4's hybrid ranking needs, since cosine
  similarity is already higher-is-better. This is the traditional-retrieval
  baseline Step 4 compares semantic search against.
  *Not derived by the user:* implemented by Claude on request (`e0f03bb`).
- 🟨 **Step 3 — Semantic search.** Embed the chunks and query them via
  ChromaDB (vector similarity). Run the same queries through both FTS and
  vector search side by side to see where each wins and loses.
  Scaffolded: `app/semantic_search.py` (stubs) and
  `tests/test_semantic_search.py` (5 failing tests). Embeddings use Chroma's
  default local model (all-MiniLM-L6-v2 via onnxruntime) — no API key and no
  per-query cost, which keeps the exercise runnable offline. Awaiting
  implementation.
- ⬜ **Step 4 — Hybrid search, reranking & retrieval evaluation.** Combine
  FTS + vector results, add a reranking step, and build a fixed eval set
  (precision/recall@k) to measure retrieval quality — reusing the
  evaluation pattern from Lab 01 Step 4, applied to retrieval instead of
  classification. The eval set is deliberately split into two query types:
  (a) queries sharing vocabulary with the target chunk, where FTS should
  already do well, and (b) paraphrased queries with little/no shared
  vocabulary (e.g. "disk filling up" vs. a chunk about "storage array
  nearing capacity"), where FTS is expected to miss and vector search is
  expected to hit. This isolates *where* semantic search earns its cost —
  recall on paraphrases, not raw query latency (vector search is slower
  per-query than FTS at this corpus size, since it requires an embedding
  API call; its advantage is retrieval quality, not speed).

## Lab 03 — Tool / Function Calling

**Objective:** Expose simulated infrastructure APIs (e.g. "restart service",
"check disk usage") to the LLM as callable tools/functions via the Claude API.

- ⬜ **Step 1 — Define simulated infrastructure tools.** Write plain Python
  functions (`restart_service`, `check_disk_usage`, `get_service_status`,
  etc.) with typed signatures and docstrings — no LLM involved yet. These are
  the "ground truth" implementations every later step wires up to the model.
- ⬜ **Step 2 — Single tool-call round trip.** Write JSON Schema tool
  definitions for the Step 1 functions, send them via `tools=[...]` on a
  Claude API call, handle the returned `tool_use` block, execute the matching
  Python function, and return a `tool_result` to get the final response.
- ⬜ **Step 3 — Multi-tool and multi-step calling.** Handle multiple tool
  calls requested in one turn (parallel tool use), and a looping
  call → execute → feed-back cycle where Claude can call more than one tool
  across multiple turns before producing a final answer.
- ⬜ **Step 4 — Input validation, error handling & tool-selection eval.**
  Validate tool inputs before executing (they come from model output, not a
  trusted caller), return `is_error` tool results on failure, and build a
  small eval set checking that the model picks the *correct* tool for a
  given incident — reusing the evaluation pattern from Lab 01 Step 4.

## Lab 04 — Model Context Protocol (MCP)

**Objective:** Build an MCP server exposing OpsPilot's tools and connect it
to an MCP-compatible client, instead of wiring tool schemas directly into
every Claude API call.

- ⬜ **Step 1 — Minimal MCP server.** Using the MCP Python SDK, build a
  server exposing a single tool (e.g. `check_disk_usage`) over stdio
  transport. Learn the server lifecycle and tool registration — no client
  yet.
- ⬜ **Step 2 — Expose the full Lab 03 tool set via MCP.** Migrate every tool
  from Lab 03 onto the MCP server, replacing the direct `tools=[...]`
  definitions sent straight to the Claude API.
- ⬜ **Step 3 — Connect an MCP client end-to-end.** Drive a full incident
  request through the MCP server (via the SDK's MCP connector or a custom
  client) instead of Lab 03's direct tool wiring. Compare the two
  architectures: what MCP buys you (standardization, reuse across clients)
  vs. its added indirection.
- ⬜ **Step 4 — Resources.** Expose the Lab 02 runbook corpus as MCP
  *resources* (not just tools), so any MCP-compatible client — not only
  OpsPilot itself — could browse the knowledge base.

## Lab 05 — Workflow Orchestration

**Objective:** Prompt chaining, routing, parallel execution, and
deterministic multi-step workflows without a heavyweight agent framework.

- ⬜ **Step 1 — Prompt chaining.** Split one complex task (e.g. "investigate
  and summarize an incident") into two sequential LLM calls, where the
  second call's prompt is built from the first call's output. Learn where
  chaining beats a single large prompt.
- ⬜ **Step 2 — Routing.** A first "router" LLM call classifies the request
  and dispatches to one of several specialized downstream prompts (e.g. a
  storage-specific vs. a backend-specific investigation flow) — conditional
  branching driven by model output rather than hardcoded logic.
- ⬜ **Step 3 — Parallel execution.** Run multiple independent LLM calls
  concurrently (e.g. checking several simulated systems at once) and
  aggregate the results. Covers the latency/cost/partial-failure trade-offs
  of fanning out LLM calls.
- ⬜ **Step 4 — Deterministic workflow evaluation.** Build a fixed set of
  scripted scenarios validating that routing decisions and chained outputs
  match expectations end-to-end — reusing the evaluation pattern once more,
  now applied to a multi-step workflow instead of a single call.

## Lab 06 — Event-Driven AI

**Objective:** Asynchronous LLM processing via Redis + RQ, retry strategies,
idempotency, and event-driven integration patterns.

- ⬜ **Step 1 — Background job queue.** Set up Redis + RQ and convert the
  synchronous incident-analysis call into an enqueued background job, with a
  polling endpoint to check job status/result.
- ⬜ **Step 2 — Retry strategy.** Configure RQ retries for transient LLM
  failures (reusing `LLMUnavailableError` from Lab 01) with exponential
  backoff, distinguishing retryable from non-retryable job failures.
- ⬜ **Step 3 — Idempotency.** Ensure a duplicate job submission (the same
  incident submitted twice) doesn't produce duplicate processing or side
  effects — introduce an idempotency-key pattern.
- ⬜ **Step 4 — Event-driven integration.** Simulate an upstream event source
  (e.g. a webhook receiving "incident created" events) that automatically
  enqueues analysis jobs, closing the loop from event → async LLM processing
  → delivered result.

## Lab 07 — Human-in-the-Loop

**Objective:** Approval workflows, authorization checks, audit logging, and
safe execution of sensitive remediation actions.

- ⬜ **Step 1 — Approval-gated actions.** Introduce a simulated remediation
  action (e.g. `restart_service`) that requires explicit human approval
  before executing: the model proposes it, a human approves/rejects via an
  endpoint, and only then does execution happen.
- ⬜ **Step 2 — Authorization.** Add a role/permission check so only certain
  users/roles can approve certain action types (e.g. high-risk actions need
  senior approval) — an authorization layer independent of the model's own
  judgment.
- ⬜ **Step 3 — Audit logging.** Record every proposed action, the decision
  (approved/rejected), who approved it, and the outcome in an audit trail —
  essential for any system where an AI recommends real-world actions.
- ⬜ **Step 4 — Safe execution guardrails.** Add pre-execution validation /
  a simulated dry-run mode, and a kill-switch to halt all automated actions
  if something looks wrong — tying approval, authorization, and audit
  logging into one coherent flow.

## Lab 08 — Agentic Workflows

**Objective:** Autonomous tool selection, multi-step reasoning, execution
limits (max steps/cost/time), and agent state management.

- ⬜ **Step 1 — Basic agent loop.** Let Claude autonomously decide which Lab
  03 tools to call and in what order to resolve an incident, without you
  hardcoding the sequence — the core "agent" pattern, contrasted with Lab
  05's hand-coded orchestration.
- ⬜ **Step 2 — Execution limits.** Add max-iteration / max-cost / max-time
  guards against runaway loops, with graceful degradation (a partial result
  plus explanation) when a limit is hit instead of a silent failure.
- ⬜ **Step 3 — State management.** Give the agent persistent state across a
  multi-turn investigation (a scratchpad of what's been tried and found) so
  it doesn't repeat failed actions or forget earlier findings.
- ⬜ **Step 4 — Agent evaluation.** Build a fixed set of simulated incident
  scenarios and measure whether the agent reaches a correct resolution
  within the execution limits — the eval pattern applied to end-to-end agent
  behavior instead of a single call.

## Lab 09 — AI Gateway, Observability & Evaluations

**Objective:** Model routing, cost tracking, tracing/execution logs,
automated evaluation pipelines, and reliability engineering for AI features.

- ⬜ **Step 1 — Cost & token tracking.** Instrument every LLM call across
  prior labs to log token usage and estimated cost per request, aggregated
  into a simple report.
- ⬜ **Step 2 — Tracing.** Add structured tracing (one span per LLM call, one
  per tool call) so a single incident's full execution path — across
  chaining, routing, and agent steps — can be reconstructed and inspected.
- ⬜ **Step 3 — Model routing.** Introduce a gateway layer that routes
  requests to different models based on request characteristics or a
  fallback policy (e.g. a cheap model for simple classification, a more
  capable one for complex investigation).
- ⬜ **Step 4 — Automated evaluation pipeline.** Consolidate the eval sets
  built across Labs 01, 02, and 08 into a single automated suite that runs
  on demand (or in CI) and reports pass/fail plus trend over time — the
  capstone quality gate for the whole system.

## Lab 10 — Agent-to-Agent Communication (optional)

**Objective:** Cooperation between independently deployed AI agents using the
A2A protocol.

- ⬜ **Step 1 — Two independent agent services.** Stand up a second,
  separate agent (e.g. a "capacity planning" agent) running as its own
  process/API, distinct from the OpsPilot incident agent.
- ⬜ **Step 2 — A2A handshake & discovery.** Implement the A2A protocol's
  agent-card and capability-discovery flow between the two agents.
- ⬜ **Step 3 — Cross-agent task delegation.** Have OpsPilot's agent delegate
  a sub-task to the other agent via A2A and incorporate its result into the
  final response.
- ⬜ **Step 4 — Reliability & evaluation.** Handle the other agent being
  unavailable gracefully (timeout/fallback), and build a test scenario
  validating the cross-agent collaboration works end-to-end.
