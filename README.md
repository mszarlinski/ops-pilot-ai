# OpsPilot AI

An AI-powered IT incident-management assistant, built incrementally as a
series of hands-on labs for learning production-grade AI/LLM integration
patterns. See `CLAUDE.md` for the project's educational goals and
collaboration rules, and `docs/learning-roadmap.md` for the full lab plan.

All infrastructure is currently simulated — no real production integrations.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in your Anthropic API key:

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `LLM_MODEL` | Claude model ID to use for classification (e.g. `claude-sonnet-5`) |

## Running the app

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000, with interactive docs at
http://127.0.0.1:8000/docs.

## Running tests

```bash
uv run pytest
```

## Running evals

The classification eval hits the real Claude API (costs money, non-deterministic)
and is skipped by default. Run it explicitly:

```bash
RUN_EVALS=1 uv run pytest tests/test_classification_eval.py -v
```

## Current status

**Lab 01 complete.** The `POST /incidents/analyze` endpoint classifies
incidents via the Claude API using structured outputs constrained to a fixed
category/severity enum, with typed error handling (503/502 for transient vs.
non-retryable upstream failures) and a measured eval (100% on the fixed
13-case set). Model ID is configurable via the `LLM_MODEL` env var.

Lab 02 (RAG) is next — see `docs/learning-roadmap.md`.
