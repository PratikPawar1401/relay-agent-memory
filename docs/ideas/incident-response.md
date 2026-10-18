# Relay: incident-response concept

Concept note, October 5, 2026. Proposed behavior only; not a completed architecture or application.

## User and problem

The intended user is a developer investigating a failing service with agent assistance. An interrupted session or handoff can lose the context of what was tried, why it failed, and which assumptions were overturned. Relay would preserve that reasoning and let the next agent continue from evidence.

The hypothesis is that shared, inspectable memory reduces repeated failed actions and improves continuity. The evaluation must test this rather than assume it.

## Demonstration narrative

1. Start a small local service sandbox and introduce a reproducible configuration fault. Use only synthetic logs and histories.
2. An investigator observes failures and develops an initial hypothesis.
3. A remediation agent attempts a plausible restart. Health remains degraded; record both the attempt and its observed failure.
4. Stop the agent processes and begin a fresh session without transferring their in-memory transcript.
5. A successor retrieves the earlier evidence and failed action from FalkorDB, then continues the unfinished investigation.
6. Reveal additional telemetry that contradicts the initial hypothesis. Preserve the old reasoning while marking it as no longer supported.
7. Traverse dependencies to identify the configuration fault, restore the known working setting, and verify service health.
8. Show the evidence path, memory update, and task handoff behind the result.

Fault injection and evidence availability can be controlled for repeatability. Label synthetic inputs explicitly. Agent choices and tool outcomes must be visible; do not describe a scripted decision as autonomous reasoning.

## Solo scope

Start with investigator and remediator roles. A replacement investigator demonstrates handoff without requiring a third distinct role. Keep one compact incident scenario and a small dependency chain.

The proposed React interface should make incident history, current task owner, and evidence behind the latest decision easy to inspect. A graph view is useful only when it explains a decision. Additional connectors, production operations, and a general memory platform are outside the initial concept.

Use the selected Python + React stack and local sandbox. The available build capacity is 40+ hours. No paid model provider or hosting service has been selected.

## Proposed measurements

| Question | Measurement |
| --- | --- |
| Does memory prevent repeated work? | Repeated failed actions after restart, with and without shared memory |
| Does the successor retain context? | Relevant earlier evidence retrieved and cited |
| Can beliefs change? | Use of superseded hypotheses after contradictory evidence arrives |
| Is coordination reliable? | Duplicate action executions and abandoned tasks under handoff/retry |
| Does remediation work? | Independent health-check result and time to recovery |
| Is the approach practical? | Model calls, token usage, ingestion time, retrieval latency |

Use the same incident, model, tools, and budgets across comparisons. Record run counts and failures. Small synthetic results support a demo claim, not broad production reliability claims.

## Unresolved research

Investigate whether the selected model follows structured tool contracts reliably; how Graphiti stores framework-managed facts; how to link those facts to explicit action history; and how task ownership can be enforced atomically. These are prerequisites to detailed implementation design.

Related notes: [Track 02](../research/track-02-memory-and-coordination.md), [Track 01](../research/track-01-connected-data.md), [framework comparison](../research/framework-comparison.md), and [graph sketch](graph-model-sketch.md).
