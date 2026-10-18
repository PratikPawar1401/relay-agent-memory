# Track 02: Agent Memory and Coordination

Research date: October 5, 2026. Primary target.

## Official focus

The track calls for memory across sessions, evolving shared state, episodic/semantic/procedural memory, conversation history, agent handoffs, concurrent access, and separation by user or tenant. These are published focus areas, not a numerical scoring rubric. [Event tracks](https://www.wemakedevs.org/hackathons/falkordb)

## Proposed mapping to Relay

The following is our concept, not organizer guidance or an implemented feature set.

| Capability | Incident-response example | Evidence to show |
| --- | --- | --- |
| Episodic memory | A restart was attempted at a specific time and did not restore health | Retrieve the attempt, tool output, and outcome after agent restart |
| Semantic memory | Checkout depends on inventory; a deployment changed configuration | Follow dependency and evidence relationships |
| Procedural memory | A recovery procedure applies only under particular conditions | Explain the procedure's preconditions and supporting successful outcome |
| Persistent conversation | Agent observations and handoff messages survive session boundaries | Fetch the earlier exchange from durable storage |
| Updating memory | Later telemetry contradicts an earlier diagnosis | Show both the earlier belief and the evidence that superseded it |
| Coordination | A replacement investigator continues unfinished work | Show task ownership and an acknowledged handoff |
| Concurrent access | Two agents attempt to claim the same remediation | Only one action executes; the other sees the current owner |
| Tenant separation | Two synthetic organizations have similarly named services | Retrieval and actions remain within the selected organization |

## Questions to investigate during implementation

**Persistence:** Separate agent-process restart from database restart tests. The first demonstrates external memory; the second also requires verified database persistence configuration. Record the exact restart procedure rather than merely opening a new chat.

**Changing facts:** Distinguish observations from inferred hypotheses. Conflicting reports should remain traceable. A later timestamp alone must not make a weak claim authoritative. Evaluate current and historical retrieval separately.

**Handoffs:** Determine what a successor needs: unresolved task, evidence references, attempted actions, outcome, and next useful check. Avoid depending on a full prompt copied from the old agent.

**Concurrency:** Memory extraction is not a task scheduler. Validate atomic task claiming, retries, stale ownership, and duplicate tool execution with the actual backend. Do not infer coordination correctness from successful parallel reads.

**Isolation:** Investigate graph-per-tenant storage and the selected framework's grouping behavior. Backend routing must enforce scope; a UI filter or agent prompt is insufficient.

## Proposed evaluation

Compare memory-enabled and memory-disabled runs using the same model, incident, available tools, and call budget. Include a simple transcript-retrieval baseline if time permits. Report all runs, including failures.

- Count repeated failed actions after a handoff.
- Measure whether the successor retrieves the relevant earlier evidence.
- Check whether an invalidated diagnosis is used as current fact.
- Count duplicate executions under contested task ownership.
- Test cross-tenant retrieval with identical service names.
- Record recovery success, tool calls, latency, and token usage.

Targets such as zero cross-tenant results and zero duplicate remediation executions are proposed acceptance criteria. They are not measured results or promises of high-concurrency performance.

## Framework boundary

Graphiti documents temporal facts, episodes, and provenance. Our coordination semantics and procedural-memory policy still need implementation and verification. See the [framework comparison](framework-comparison.md) and [concept note](../ideas/incident-response.md).
