# OpsPilot AI

An AI-powered IT incident-management assistant, built incrementally as a
series of hands-on labs for learning production-grade AI/LLM integration
patterns. See `CLAUDE.md` for the project's educational goals and
collaboration rules, and `docs/learning-roadmap.md` for the full lab plan.

All infrastructure is currently simulated — no real production integrations.

## Branch structure

- **`main`** (this branch) — lesson material only. No application code yet.
  Start here.
- **`solutions`** — the full worked implementation, lab by lab, for
  reference after you've attempted each exercise yourself.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

Copy `.env.example` to `.env` and fill in your Anthropic API key (needed
starting from Lab 01 Step 2, once you're calling a real LLM):

```bash
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `LLM_MODEL` | Claude model ID to use for classification (e.g. `claude-sonnet-5`) |

## Current status

**Nothing built yet.** Start with Lab 01, Step 1 in `docs/learning-roadmap.md`.
