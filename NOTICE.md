# Third-party attribution

Relay includes modified code from **Cognee**, Copyright 2024 Topoteretes UG,
licensed under Apache License 2.0. This project includes software developed at
Topoteretes UG (https://www.cognee.ai/).

Adapted components: hybrid reciprocal-rank fusion with importance weighting, and
graph triplet context formatting. Upstream revision:
`37f788bd287750e10d7610173e5332b3843f6ebd`.

See [license](src/relay/_vendor/cognee/LICENSE),
[upstream notice](src/relay/_vendor/cognee/NOTICE.md),
[source provenance and hashes](src/relay/_vendor/cognee/PROVENANCE.json), and
[modified implementation](src/relay/_vendor/cognee/retrieval.py).

Relay's adapters use lexical and graph-evidence ranking lanes instead of Cognee's
vector/summary lanes. Relay implements incident scope, evidence pinning, context
budget, provenance storage, ownership guards, worker lifecycle and sandbox recovery.
This is a narrow derived component, not the full Cognee platform, an official
Cognee integration, or a claim of endorsement.
