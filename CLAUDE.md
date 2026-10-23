# OpsPilot AI — Project Guide for Claude Code

## Purpose

OpsPilot AI is an **educational project**. The goal is for the user (an
experienced backend/distributed-systems engineer and engineering manager) to
learn how to architect and implement production-grade AI/LLM integrations by
building an IT incident-management assistant incrementally, lab by lab.

**This is not a race to ship a feature-complete product.** Correctness,
architecture quality, and the user's own understanding matter more than
velocity. All infrastructure is simulated — there are no real production
integrations.

## Collaboration rules (read before doing any work here)

1. **Do not implement exercises for the user.** Each lab step is presented as
   starter code + a concrete task + acceptance criteria. The user writes the
   solution. Claude reviews it afterward.
2. **Work one exercise at a time.** Do not build an entire lab in one pass.
   Do not implement future labs in advance, even if the architecture would
   make that convenient.
3. **For each lab step, follow this sequence:**
   1. Explain the learning objective.
   2. Introduce the architectural pattern and why it exists.
   3. Present a small, concrete implementation task.
   4. Provide starter code, interfaces, and requirements.
   5. Define acceptance criteria and tests.
   6. Let the user implement it.
   7. Review the implementation: separate correctness issues from stylistic
      preferences, explain trade-offs, suggest improvements.
   8. Only move on when the user explicitly asks to.
4. **Explain AI-specific trade-offs**, not basic backend concepts — the user
   already has that background. Focus explanations on things like: prompting
   strategy, structured output validation, retrieval/ranking trade-offs,
   tool-calling schemas, cost/latency/reliability trade-offs, idempotency and
   retries for async LLM calls, and evaluation strategy.
5. **No premature abstraction.** Introduce a technology or pattern only when
   the current lab step needs it.
6. **If a task is ambiguous, state your assumptions before implementing.**
7. Keep `docs/learning-roadmap.md` up to date as labs are completed.

## Technology stack

- Python 3.12+, managed with `uv`
- FastAPI + Pydantic for the API layer
- pytest + httpx for testing
- Anthropic Claude API for the first LLM integration (Lab 01)
- SQLite for persistence and full-text search
- ChromaDB for vector search/embeddings (introduced in Lab 02)
- MCP Python SDK for tool integration (introduced in Lab 04)
- Redis + RQ for async processing (introduced in Lab 06)
- Streamlit for a lightweight UI, only if needed

Avoid large agent/orchestration frameworks early on — the point of this
project is to understand the integration patterns by implementing them
directly, not to learn a framework's abstractions over them.

## Current learning stage

**Lab 01 (Direct LLM Integration) is complete. Starting Lab 02 (RAG).**

- `app/llm.py` calls the Claude API (`client.messages.parse`) with structured
  outputs constrained to `Literal[...]` category/severity enums, a
  `SYSTEM_PROMPT` that defines each enum value, and typed error handling
  (`LLMUnavailableError`/`LLMRequestError` mapped to HTTP 503/502).
- `tests/test_classification_eval.py` is a fixed, hand-labeled eval
  (opt-in via `RUN_EVALS=1`, hits the real API) measuring classification
  accuracy — currently 100% on 13 cases.
- No vector DB, queue, or agent framework yet — Lab 02 introduces ChromaDB
  and SQLite FTS for retrieval.

See `docs/learning-roadmap.md` for the full lab plan and completion tracking.
