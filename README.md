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

## Current status

Lab 01, Step 1: project bootstrap. The `POST /incidents/analyze` endpoint
exists but its classification logic is intentionally unimplemented (returns
HTTP 501) until the first exercise is completed.
