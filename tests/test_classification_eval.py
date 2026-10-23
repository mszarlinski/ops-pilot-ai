"""Evaluation of the real Claude-backed classifier against a fixed, hand-labeled
dataset.

Unlike the rest of the test suite, this calls the real Claude API — it costs
money, is non-deterministic, and needs ANTHROPIC_API_KEY set. It is skipped
by default; run it explicitly with:

    RUN_EVALS=1 uv run pytest tests/test_classification_eval.py -v

Use it to measure whether a system-prompt change actually improved
classification accuracy, instead of eyeballing a few manual API calls.
"""

import os

import pytest

from app.llm import classify_incident

pytestmark = pytest.mark.skipif(
    "RUN_EVALS" not in os.environ,
    reason="Set RUN_EVALS=1 to run real-API evals (costs money, needs ANTHROPIC_API_KEY)",
)

# (description, expected_category, expected_severity)
# Covers all 5 categories (STORAGE, BACKEND, NETWORK, UI, OTHER) and all 3
# severities (LOW, MEDIUM, HIGH). Several cases deliberately avoid obvious
# keywords ("timeout", "storage") to test whether the model (and the prompt's
# category definitions) generalize the underlying concept, rather than
# pattern-matching one keyword like the Step 1 deterministic classifier did.
EVAL_CASES = [
    # STORAGE
    ("Database connection timeout on prod-db-01 for the last 15 minutes", "STORAGE", "HIGH"),
    ("S3 bucket ops-pilot-uploads is returning 503 errors on every PUT request", "STORAGE", "HIGH"),
    ("Disk usage on the archive storage array is at 92% and climbing steadily", "STORAGE", "MEDIUM"),
    ("Nightly backup job to cold storage failed with a checksum mismatch", "STORAGE", "HIGH"),
    # BACKEND
    ("Checkout API is returning HTTP 500 for every purchase attempt", "BACKEND", "HIGH"),
    ("Background job queue processing confirmation emails is running 20 minutes behind", "BACKEND", "MEDIUM"),
    # NETWORK
    ("VPN connectivity to the EU data center is down, blocking all remote engineer access", "NETWORK", "HIGH"),
    ("Intermittent packet loss between app servers and the Redis cache cluster is causing occasional slow requests", "NETWORK", "MEDIUM"),
    # UI
    ("Primary navigation menu on the customer portal does not respond to clicks, preventing users from reaching any other page", "UI", "HIGH"),
    ("User reports the dashboard logo is slightly misaligned on Safari", "UI", "LOW"),
    ("Login page layout is broken on narrow mobile viewports", "UI", "LOW"),
    # OTHER — genuinely doesn't fit STORAGE/BACKEND/NETWORK/UI, unlike a footer
    # typo (UI) or search ordering (BACKEND), which were mislabeled here
    # earlier and are now correctly STORAGE/BACKEND/UI cases above instead.
    ("New hire's badge access request was never provisioned by the IT helpdesk", "OTHER", "LOW"),
    ("Status page was not updated during last week's outage, confusing customers", "OTHER", "MEDIUM"),
]

ACCURACY_THRESHOLD = 0.9


def test_classification_accuracy_meets_threshold():
    correct = 0
    failures = []

    for description, expected_category, expected_severity in EVAL_CASES:
        result = classify_incident(description)
        is_correct = result.category == expected_category and result.severity == expected_severity
        if is_correct:
            correct += 1
        else:
            failures.append(
                f"{description!r}: expected ({expected_category}, {expected_severity}), "
                f"got ({result.category}, {result.severity})"
            )

    accuracy = correct / len(EVAL_CASES)
    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Accuracy {accuracy:.0%} below {ACCURACY_THRESHOLD:.0%} threshold. Failures:\n"
        + "\n".join(failures)
    )
