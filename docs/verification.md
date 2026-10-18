# Verification

Relay is verified through automated unit, integration, concurrency, recovery, and build checks.

## Reproducible checks

```sh
uv sync --locked --all-extras
docker compose up -d --wait
RELAY_INTEGRATION=1 uv run pytest -q
uv run ruff check src sandbox tests
npm --prefix frontend ci
npm --prefix frontend run build
```

The suite covers tenant and incident boundaries, competing claims, fencing tokens, failed-action guards, replay, receipt correlation, lost-response reconciliation, retrieval provenance, citation validation, process separation, persistence, and the full retrieval-to-recovery path.

## Demonstrated results

- The complete deterministic workflow reaches `resolved` only after an independent checkout HTTP probe passes.
- A local Mistral successor retrieved FalkorDB history, cited stored evidence, selected `restore_inventory_route`, and produced a correlated recovery receipt.
- The three-pair memory ablation produced valid, safely handed-off, cited decisions in every history-enabled run.
- FalkorDB persistence retained the full incident snapshot across a database-container restart.
- The browser console completed all four stages and displayed the new worker identity, retrieved context, graph paths, citations, action receipt, and recovery proof.
- A clean clone installed from the committed lockfiles and passed integration tests, lint, and the frontend production build.
- Gemini contract tests cover structured output validation, blocked responses, empty candidates, configuration, and model readiness probing.

## Evaluation artifact

[`artifacts/evaluation/mistral-history-ablation.json`](../artifacts/evaluation/mistral-history-ablation.json) contains the complete paired outputs and measured provider metadata.
