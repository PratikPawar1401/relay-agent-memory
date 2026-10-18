# Memory framework comparison

Relay uses FalkorDB directly for authoritative incident memory and coordination, plus a narrow attributed Cognee-derived retrieval layer.

| Capability | Graphiti | Cognee | Direct FalkorDB | Relay choice |
| --- | --- | --- | --- | --- |
| FalkorDB integration | Supported backend | Community integration available | Native client | Direct client for core state |
| Temporal memory | Framework-managed episodes and facts | Knowledge pipelines and graph memories | Application-defined | Explicit validity windows and immutable episodes |
| Provenance | Episodes and facts | Pipeline and graph sources | Application-defined | `SUPPORTS`, `CONTRADICTS`, and `CITES` relationships |
| Coordination | Application layer | Application layer | Full query-level control | Conditional Cypher claims and fencing tokens |
| Retrieval | Hybrid framework search | Graph and vector pipelines | Custom queries | Cognee-derived rank fusion over FalkorDB evidence |
| Runtime footprint | Framework plus provider clients | Framework plus provider clients | FalkorDB client | Small direct core with optional model providers |
| Cost control | Depends on configured providers | Depends on configured providers | Local graph operations | Local FalkorDB and Mistral, with explicit Gemini selection |

## Implemented boundary

Relay owns tenant and incident scoping, episodes, current and historical hypotheses, procedures, ownership, actions, receipts, and reconciliation. The retrieval component adapts Cognee reciprocal-rank fusion and graph-triplet formatting. Exact upstream revisions, hashes, license text, and modifications are stored with the vendored files.

Graphiti remains available as a semantic-memory extension. Relay's main judging path stays directly inspectable through FalkorDB and the attributed Cognee-derived component.

## Sources

1. [Graphiti](https://github.com/getzep/graphiti)
2. [Cognee](https://github.com/topoteretes/cognee)
3. [FalkorDB Python client](https://github.com/FalkorDB/falkordb-py)
4. [Relay Cognee component note](../cognee-memory.md)
