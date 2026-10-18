# Cognee-derived memory component

Relay contains a small, attributed adaptation of two Apache-2.0 Cognee retrieval utilities. It is deliberately narrower than the Cognee platform: FalkorDB remains Relay's authoritative store, and Relay owns tenant and incident scoping, temporal policy, safety-critical evidence pinning, context limits, citations, action guards, and worker handoffs.

## What was adapted

- Reciprocal-rank fusion and bounded importance weighting from Cognee's hybrid ranking utility.
- Graph triplet formatting from Cognee's brute-force triplet search utility.

The modified implementation is in [`src/relay/_vendor/cognee/retrieval.py`](../src/relay/_vendor/cognee/retrieval.py). The upstream revision, source URLs, and SHA-256 hashes are recorded in [`PROVENANCE.json`](../src/relay/_vendor/cognee/PROVENANCE.json). The original Apache-2.0 license and notice are preserved beside the code, and the project-level attribution is in [`NOTICE.md`](../NOTICE.md).

## Relay retrieval flow

1. Query at most 256 episodes linked to the requested incident.
2. Build a lexical rank and a graph-evidence rank.
3. Fuse those ranks with the adapted reciprocal-rank function.
4. Pin the newest configuration and every failed-action receipt so ranking cannot hide safety facts.
5. Add current hypotheses, dependency paths, procedures, and failed actions from FalkorDB.
6. Enforce an 18 KB context budget, failing closed if mandatory evidence alone exceeds it.
7. Persist the selected episode IDs, rank reasons, graph triplets, byte size, upstream revision, and SHA-256 context hash.
8. Create `CITES` edges from the retrieval manifest and decision to the actual source episodes.

No embeddings, Cognee runtime service, external model, or second database is used by this component. Documented behavior and passing tests establish only this local adaptation. It should be described as **Cognee-derived**, not as Cognee itself or an official integration.

## Why this shape fits Relay

The demo needs deterministic, auditable retrieval under a short build window. Lexical and graph ranking are inspectable, while mandatory evidence pinning prevents a high-scoring but incomplete context from omitting the failed restart or current configuration. The full framework remains a future option if evaluation shows that embeddings or automated extraction improve retrieval without weakening incident isolation and provenance.

## Verification

`tests/test_recall.py` verifies stable rank fusion, null-safe triplet formatting, incident isolation, evidence pinning, context limits, stored retrieval manifests, `CITES` edges, and distinct worker processes. Run the full suite with:

```sh
RELAY_INTEGRATION=1 uv run pytest -q
```
