# Relay — incident memory that survives an agent handoff

Track 02: Agent Memory and Coordination. Python + React, FalkorDB operational memory, and a **Cognee-derived retrieval component**.

Relay records a failed incident repair, hands ownership to a fresh worker, retrieves the relevant evidence, lets local Mistral choose a bounded next action, and verifies the repair through a real synthetic HTTP service. The console shows worker process IDs, retrieved episodes, citations, graph paths and receipts.

## Run locally

Requirements: Docker Compose, uv, Python 3.12, and Node 24 (tested: 24.22.0). Free ports: 6380, 3001, 8091, 8088 and 5173. These services bind to loopback. No API key or paid account is required for the deterministic demo or retrieval.

```sh
make setup
make services
make api
```

In a second terminal:

```sh
make web
```

Open **http://127.0.0.1:5173**. Initialize a case, run Agent A, verify the guard, then launch the successor. The console detects local Mistral when available; otherwise select **Controlled policy**, which is explicitly deterministic and makes no AI call. All console stages run in fresh Python worker processes. Current case state refreshes every two seconds.

For a terminal-only deterministic demonstration:

```sh
uv run relay demo
```

For a real model decision, run your existing Ollama-compatible server with `mistral:latest` at port 11434, then:

```sh
uv run relay demo --provider ollama
```

Override `RELAY_OLLAMA_URL` / `RELAY_OLLAMA_MODEL` as needed. Missing models fail explicitly; there is no paid provider fallback. Agent A and the diagnosis-update workflow are controlled application logic; only the successor's bounded action choice is model-generated.

## Cognee-derived memory

The successor uses `relay.recall.retrieve`, which queries only its incident in its tenant's FalkorDB graph. It combines lexical relevance and graph evidence using **actual adapted Cognee reciprocal-rank fusion code**, pins current configuration and failed attempts, and builds graph-triplet context using Cognee's adapted formatter. It stores the selected IDs, ranking reasons, context size/hash, source revision and worker identity before asking the model.

This is a narrow derived component, not an installation of the full Cognee platform. It does not require embeddings and does not claim semantic vector retrieval. The code, Apache 2.0 license, upstream notice, source hashes and modification description are in [the vendor directory](src/relay/_vendor/cognee/) and [NOTICE.md](NOTICE.md).

[Component design and reuse boundary](docs/cognee-memory.md) · [Executable retrieval](src/relay/recall.py) · [Operational Cypher](src/relay/queries.py).

## Inspect, reopen and recover

The console includes memory search, clickable evidence references, actual dependency paths and procedure conditions, and a saved-context manifest. Search previews are explicitly separate from context actually supplied to the model. Use **Open an existing case** with its tenant and incident IDs to reopen it. Transient errors preserve the saved case reference.

```sh
uv run relay context --tenant TENANT --incident INCIDENT
uv run relay recall --tenant TENANT --incident INCIDENT --query 'Which restart failed?'
uv run relay reconcile --tenant TENANT --incident INCIDENT
```

A running operation may have executed even if its response was lost. **Reconcile receipt** looks up the existing operation and finalizes only a matching completed receipt; it never dispatches the tool again. Missing/incomplete receipts remain uncertain and require manual sandbox inspection. A confirmed failure before action dispatch releases the claim. Completed first-shift, guard and resolved-resume requests replay without new effects.

If sandbox initialization failed after creating the incident, its ID appears in the error; retry with `uv run relay initialize --tenant TENANT --incident INCIDENT`. Start with a fresh case when testing the updated contracts against old demo data.

FalkorDB Browser: http://localhost:3001. API docs: http://localhost:8088/docs. `docker compose down` retains named volumes; `down -v` discards them.

For a public console deployment, see [Vercel deployment](docs/deployment-vercel.md). The prepared title, submission copy, and three-minute recording script are in [the submission package](docs/submission.md). The learning narrative is in [What I learned building Relay](docs/blog-what-i-learned-building-relay.md).

## Gemini workflow

Copy `.env.example` to `.env`, set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and `RELAY_GEMINI_MODEL`, then verify the configured model:

```sh
uv run --env-file .env relay provider-check --provider gemini
uv run --env-file .env uvicorn relay.api:app --host 127.0.0.1 --port 8088
# Terminal-only end-to-end run:
uv run --env-file .env relay demo --provider gemini
```

Relay probes the selected Gemini model before enabling it in the console. The successor uses Gemini structured JSON output, validates the returned tool and evidence IDs, stores provider usage metadata, and preserves the incident for another handoff when the provider declines or cannot complete a decision.

## Verification and evaluation

```sh
make test
make build
# Optional: paired real-model decisions, no model-proposed repair execution.
uv run relay evaluate --provider ollama --runs 3
```

Integration tests use disposable graph namespaces and real local sandbox services. They cover claims, fencing, tenant/incident boundaries, process separation, replay, evidence validity, receipt correlation, lost-response reconciliation and the full retrieval-to-repair flow. Optional Graphiti tests skip when its extra is not installed.

The evaluation alternates with-history and without-history calls while keeping current evidence, procedure, model settings, and action budget fixed. In the recorded three-pair local-Mistral run, graph history produced three valid, safely handed-off decisions with exact episode citations. The [per-run artifact](artifacts/evaluation/mistral-history-ablation.json) contains the complete prompts, outputs, validation results, and usage data.

See [architecture](docs/implementation.md), [verification](docs/verification.md), and [Cognee release notes](docs/cognee-memory.md).

## Demonstrated scope

Relay demonstrates the complete restart-and-handoff scenario with tenant-scoped graphs, atomic ownership claims, durable action receipts, bounded retrieval, cited model decisions, and independent HTTP recovery verification. The synthetic sandbox makes every state transition repeatable for judging.

The [public source repository](https://github.com/PratikPawar1401/relay-agent-memory) is live and its GitHub Actions verification passes. The prepared recording sequence and submission copy are in [the submission package](docs/submission.md).

## Research index

| Document | Purpose |
| --- | --- |
| [Rules and submission](docs/research/rules-and-submission.md) | Event requirements and submission checklist |
| [Track 02 research](docs/research/track-02-memory-and-coordination.md) | Memory, coordination, and proposed evidence of success |
| [Track 01 research](docs/research/track-01-connected-data.md) | Connected reasoning and sandbox actions |
| [Framework comparison](docs/research/framework-comparison.md) | Graphiti, Cognee, and direct FalkorDB tradeoffs |
| [Lessons from Scrape-Verse winners](docs/research/winner-strategies.md) | Verified winners, transferable strategies, and demo priorities |
| [Source register](docs/research/sources.md) | Primary references and supported claims |
| [Incident-response concept](docs/ideas/incident-response.md) | User problem, demo narrative, scope, and measurements |
| [Graph model sketch](docs/ideas/graph-model-sketch.md) | Candidate entities, relationships, and retrieval questions |

## AI assistance and attribution

Codex assisted with research, implementation, tests and debugging. All incident fixtures are synthetic. Cognee-derived code is explicitly attributed in [NOTICE.md](NOTICE.md); our original contribution includes the incident workflow, FalkorDB adapter, evidence policy, coordination, reconciliation and interface. Dependencies are pinned in `uv.lock` and `frontend/package-lock.json`.
