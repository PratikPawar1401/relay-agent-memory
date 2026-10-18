# Memory framework comparison

Research date: October 5, 2026. **Documentation review only: no integration has been installed or tested locally.**

Update October 15: the statement above describes the original research date. See [current verification](../verification.md) for the installed versions and tested Graphiti driver/FalkorDB integration. Semantic extraction remains unverified.

## Evidence and tradeoffs

| Dimension | Graphiti + FalkorDB | Cognee + FalkorDB | Direct FalkorDB client |
| --- | --- | --- | --- |
| Integration evidence | Repository documents a FalkorDB extra and driver [1] | Community hybrid adapter is documented [2] | Official Python client [4] |
| Memory ingestion | Episodes and incremental fact extraction [1] | Add/cognify/search pipeline in adapter example [2] | Application must implement ingestion |
| Temporal memory | Validity windows and historical fact handling documented [1] | Adapter support alone does not establish temporal semantics | Application must model validity and updates |
| Provenance | Episode-to-fact lineage documented [1] | Verify what survives ingestion and retrieval | Explicit evidence relationships are our responsibility |
| Retrieval | Hybrid semantic, keyword, and graph retrieval [1] | Adapter supports graph and vector storage [2] | Cypher plus available indexes; retrieval logic is ours [5] |
| Coordination | Task claiming and action deduplication remain application work | Same; do not treat ingestion as coordination | Full control, but all coordination logic is ours |
| Dependencies | Python framework, backend, inference and embedding configuration | Cognee, adapter registration, backend, model configuration; example also uses SQLite | Python client and backend; model calls are optional until agent behavior is added |
| Cost considerations | Ingestion and embedding calls may incur provider charges | Same; measure calls per ingestion | Fewer framework calls possible, but more implementation work |

The tradeoffs above are our assessment. No comparative benchmark or verified version combination exists for this project yet.

## Recommendation

Investigate Graphiti first for evolving incident evidence. Retain direct FalkorDB access for application-owned tasks and action history, subject to validating graph layout and ownership boundaries. Avoid concurrent direct writes into framework-managed structures without understanding their invariants.

Cognee remains an alternative if runbook/document ingestion becomes the dominant requirement. Do not run two memory frameworks in the first version: reconciling duplicated entities and competing state would expand the solo workload.

## Compatibility risks

- Cognee issue #142 reports interface and configuration gaps for **Cognee 1.3.0 with adapter 0.3.1**. This is a version-specific report, not proof that every release is broken. Recheck resolution and selected versions before use. [3]
- The adapter README and other examples may differ in provider naming or configuration. Resolve names against the selected release's registration code rather than combining snippets.
- Graphiti documentation is not a guarantee that every driver feature behaves identically across backends. Test grouping, custom types, retrieval, and updates on FalkorDB.
- Pin the working framework, driver, and server versions after validation; do not claim compatibility based on an unpinned latest installation.

## Event-time validation checklist

1. Ingest a small synthetic episode and retrieve its evidence from FalkorDB.
2. Add a conflicting update and inspect current versus historical retrieval.
3. Restart the application process and retrieve the same memory.
4. Check two tenant scopes with overlapping entity names.
5. Inspect the actual stored graph and verify the application can explain its query paths.
6. Measure ingestion calls, retrieval latency, and errors on a modest fixture.
7. Validate application coordination separately with simultaneous claims and retries.

If Graphiti fails a critical check, timebox diagnosis before evaluating a minimal direct-client memory implementation. Exact fallback scope is an event-time decision.

## Cost posture

No paid services are approved. A local backend avoids managed-hosting usage, but model inference and embeddings require their own cost assessment. Free credits and local-model feasibility remain unconfirmed. Avoid publishing cost or latency estimates until measured.

## Primary references

1. [Graphiti repository and documentation](https://github.com/getzep/graphiti)
2. [Cognee community FalkorDB adapter](https://github.com/topoteretes/cognee-community/blob/main/packages/hybrid/falkordb/README.md)
3. [Cognee adapter compatibility report #142](https://github.com/topoteretes/cognee-community/issues/142)
4. [FalkorDB Python client](https://github.com/FalkorDB/falkordb-py)
5. [FalkorDB documentation](https://docs.falkordb.com/)
