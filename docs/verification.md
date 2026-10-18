# Verification record

Initial backend milestone, October 15, 2026; current build verified October 18. These are local observations, not performance benchmarks or production guarantees.

## Environment

- macOS arm64 host, Python 3.12.13.
- FalkorDB container `v4.20.1`, Python client `1.8.0`.
- Graphiti `0.30.2`; resolved dependencies in `uv.lock`.
- Local `mistral:latest` (7.2B, Q4_K_M) via Ollama-compatible HTTP service.
- Separate project ports; existing Redis/Postgres services were not changed.

## Recorded results

- Final automated run: **36 tests passed**; Ruff checks passed. Integration tests used real local FalkorDB and sandbox services, including replay safety, typed evidence, uncertain-operation reconciliation, retrieval provenance, process separation, and the staged console workflow.
- The React/TypeScript production build passed. A live Chrome walkthrough completed all four console stages and visibly reached `resolved`, `completed`, and `HTTP verified` state with a persisted health receipt.
- The deterministic demo passed: controlled restart failed; a fresh process recovered the failed-action memory, superseded the initial diagnosis, restored the route, and passed an independent checkout health probe.
- A local Mistral successor selected `restore_inventory_route`, cited a real configuration episode, and recovered the service. One observed call used 2,447 input tokens and 119 output tokens, with approximately 22.6 seconds reported by the runtime. This single run is not an accuracy or latency benchmark.
- The first Mistral call using JSON Schema failed with the local runtime's grammar-parser error. The runner safely handed off without dispatching a corrective action. JSON mode plus Pydantic/citation validation succeeded on retry. No hidden model fallback was used.
- Graphiti's actual FalkorDB driver built indexes and read back a probe node. This did not call a model and does not validate semantic ingestion/search.
- FalkorDB reported `appendonly=yes` and `appendfsync=always`.
- After restarting only Relay's FalkorDB container, the saved Mistral demo snapshot matched exactly: 12 episodes, two actions, and all incident/task/hypothesis state. Snapshot comparison artifacts are local and ignored by version control.
- The live API at `http://localhost:8088/health` returned `status: ok` with `memory: falkordb`.
- The React/TypeScript production build passed on October 18 after the final stage and recall changes.
- A three-pair `mistral:latest` ablation kept the current observation, restart procedure, model settings, and action budget fixed. With history, all three outputs were valid safe handoffs that cited the current probe and a handoff summary. Without history, all three outputs attempted restart but nested the response incorrectly and failed strict schema validation. No proposed action was executed. This demonstrates fail-closed behavior and a history-conditioned valid choice, but it is not a clean accuracy comparison. The citation-quality gap remains: history runs did not cite the failed-action receipt itself.
- After adding an explicit copyable evidence catalog and dynamic forbidden-tool list, a fresh browser case completed in one successor attempt with local Mistral. It cited the current configuration episode, chose `restore_inventory_route`, produced a correlated receipt, and reached `resolved` only after the checkout probe passed. The resolved case prefix is `1fb1d6ed`; the console remains open locally.

## Reproduction

```sh
uv sync --locked --all-extras
docker compose up -d --wait
RELAY_INTEGRATION=1 uv run pytest -q
npm --prefix frontend install
npm --prefix frontend run build
uv run relay demo
uv run relay demo --provider ollama
uv run relay graphiti-probe --tenant graphiti-check
```

The test suite records correctness at small scale. Tests with concurrent independent claimants establish the tested claim guard behavior, not a high-throughput concurrency benchmark.

## Evaluation artifact

[`artifacts/evaluation/mistral-history-ablation.json`](../artifacts/evaluation/mistral-history-ablation.json) contains the six recorded model outputs and measured metadata. It is a small synthetic decision-only experiment; `recovery_success` is deliberately `null` because model proposals were never dispatched.

## Not yet established

Gemini free-tier behavior; Graphiti extraction/contradiction quality; authenticated tenant isolation; production recovery from incomplete external operations; public deployment; and the final demo video. No Gemini key was read or used in this milestone.
