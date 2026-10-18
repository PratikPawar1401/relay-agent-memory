# Track 01 — connected data and actions

Relay also demonstrates graph-backed reasoning and action selection.

## Connected reasoning

- Traverse `checkout → inventory → warehouse` dependencies from FalkorDB.
- Link observations to hypotheses with `SUPPORTS` and `CONTRADICTS`.
- Link model decisions to the exact episodes they cite with `CITES`.
- Retrieve procedures connected to the affected service.

## Graph-backed actions

The corrective route action is eligible only when FalkorDB supplies a matching procedure and current configuration evidence. Conditional writes enforce ownership and prevent a repeated failed restart. The action receipt and final health probe are written back into the same evidence graph.

## Judge-visible evidence

The console renders the returned dependency path, procedure, belief history, selected episodes, citations, action receipt, and verification event. This makes the graph part of the decision and recovery workflow.
