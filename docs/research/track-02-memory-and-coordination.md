# Track 02 — agent memory and coordination

Relay maps the track's memory types to a concrete incident-response workflow.

| Memory type | Relay representation | Demonstration |
| --- | --- | --- |
| Episodic | Immutable observations, handoffs, decisions, receipts, and verification events | The successor recalls what Agent A observed and attempted |
| Semantic | Services, dependencies, configurations, and evolving hypotheses | A configuration observation supersedes the initial process hypothesis |
| Procedural | Named recovery procedures with structured preconditions and targets | The route-repair procedure becomes eligible from current evidence |

## Coordination

- Conditional FalkorDB writes grant one worker a fenced claim.
- Each stage runs in a fresh Python process with a persisted run ID and PID.
- Stale ownership tokens are rejected.
- Failed actions remain linked to their receipts and cannot be repeated for the incident.
- Reconciliation retrieves the original durable receipt by operation ID.
- Tenant and incident graph scope is applied to every retrieval and mutation.

## Retrieval and changing facts

The successor receives a bounded context assembled from FalkorDB. Cognee-derived reciprocal-rank fusion combines lexical and graph evidence. Current configuration and failed-action receipts are pinned, while hypotheses retain validity windows so the console can display both the previous belief and the current one.

## Measured proof

The integration suite exercises contested claims, fencing, scope boundaries, replay, reconciliation, citation validity, and the full handoff-to-recovery flow. The paired model artifact keeps current evidence, tools, model settings, and call budget fixed while changing whether incident history is supplied.
