# Graph Hacks submission package

## Entry

- **Project:** Relay
- **Primary track:** Track 02 — Agent Memory and Coordination
- **Secondary track:** Track 01 — Connected Data and Actions
- **One-line pitch:** Relay gives a fresh incident-response agent durable, scoped memory of evidence, failed actions, procedures, and handoffs so it can continue safely instead of repeating the previous worker's mistake.

## Repository presentation

Suggested repository name: `relay-agent-memory`.

Suggested description:

> FalkorDB-backed incident memory and safe agent handoffs with Cognee-derived retrieval, bounded actions, and independently verified recovery.

Suggested topics: `falkordb`, `agent-memory`, `multi-agent`, `knowledge-graph`, `incident-response`, `cognee`, `fastapi`, `react`, `hackathon`.

The public repository is [PratikPawar1401/relay-agent-memory](https://github.com/PratikPawar1401/relay-agent-memory). Branch `main` has pinned CI actions and passes the public install, integration-test, lint, and frontend-build workflow.

## Three-minute recording

1. **0:00–0:20 — Problem.** Checkout is unavailable. Explain that the first worker can disappear with context trapped in its prompt.
2. **0:20–0:50 — Agent A.** Run the controlled first shift. Show the failed restart receipt and the worker PID/run ID.
3. **0:50–1:10 — Guard.** Attempt the recorded unsafe repeat. Show FalkorDB rejecting it before an external tool call.
4. **1:10–1:55 — Fresh successor.** Launch Gemini or local Mistral. Show a different PID, the selected episodes, context hash, dependency path, and procedure.
5. **1:55–2:25 — Recovery.** Show the cited decision, route restoration receipt, and independent checkout health probe.
6. **2:25–2:45 — Graph proof.** Show the temporal hypothesis history and the source-to-decision evidence links.
7. **2:45–3:00 — Evidence.** Show the passing checks, paired evaluation artifact, synthetic-data disclosure, AI-assistance disclosure, and public source.

Record a deterministic-policy backup immediately after the Mistral take. Label it visibly as policy mode; do not imply that it is an AI decision.

## Submission copy

### Problem

Incident agents often lose operational context at process boundaries. A successor may repeat a failed action, rely on stale beliefs, or claim recovery without a trustworthy receipt.

### Solution

Relay stores incident episodes, hypotheses, procedures, ownership, actions, receipts, and verification in tenant-scoped FalkorDB graphs. Independent worker processes claim work with fencing tokens. A successor retrieves bounded incident context using an attributed Cognee-derived rank-fusion component, cites exact episodes, chooses one allowlisted action, and resolves the incident only after an independent HTTP probe.

### Why FalkorDB is central

FalkorDB is the authoritative memory and coordination layer. Conditional Cypher writes arbitrate claims, reject stale workers, prevent repeated failed actions, retrieve service dependencies and procedures, retain superseded hypotheses, and connect decisions to evidence. The application fails closed when FalkorDB is unavailable.

### Demonstrated scope

Relay demonstrates durable episodic, semantic, and procedural memory, cross-process handoff, guarded actions, durable receipts, and independently verified recovery through a repeatable synthetic checkout incident.

The recorded Gemini run supplies direct provider evidence: the successor cited the failed restart result and current configuration, selected the graph-eligible repair, and resolved the incident after an independent probe.

### Disclosures

All incident data is synthetic. Codex assisted with research, implementation, testing, and debugging. The participant reviewed the implementation and is responsible for the submission. Relay includes a narrow modified component derived from Cognee under Apache-2.0; exact source revisions, hashes, license, notices, and modifications are included in the repository.

## Public source

https://github.com/PratikPawar1401/relay-agent-memory
