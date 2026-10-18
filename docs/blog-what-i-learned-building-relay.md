# What I Learned Building Relay: Memory Is More Than a Prompt

I built Relay for the FalkorDB Graph Hacks Track 02: Agent Memory and Coordination. The idea was simple: an incident agent should not lose the work of a previous agent just because the process ended.

Relay records a failed incident repair, hands the task to a fresh worker, retrieves the relevant evidence from FalkorDB, chooses a bounded next action, and verifies the repair against a synthetic checkout service. The console shows the timeline, ownership, evidence, graph relationships, decision, and receipt.

The project taught me that durable agent memory is not primarily a prompt-engineering problem. It is a state, coordination, evidence, and recovery problem.

## 1. A handoff is a protocol, not a longer prompt

The first version of the idea was close to “save the conversation and give it to the next agent.” That is not enough. A successor needs to know:

- what was observed;
- which hypotheses were active or superseded;
- which actions were attempted;
- what failed and why;
- who currently owns the task;
- whether an external operation might still be running; and
- which evidence is allowed to support the next action.

Relay models those facts as graph entities and relationships instead of treating the handoff as an unstructured transcript. That makes the handoff inspectable and gives the application something stronger than “the model remembers.”

## 2. Persistence and intelligence are different claims

A system can persist memory correctly without proving that memory improves a model's decision. Relay's initial scenario made this distinction especially clear: the current configuration exposed enough information for a successor to infer the repair even without historical context.

The evaluation compares identical model calls with and without historical memory while keeping current observations, tools, budgets, and prompts controlled. It records proposed actions separately from executed actions so memory-conditioned decisions and guard behavior remain independently measurable.

This became one of the most important lessons from the project: measure the central claim directly, even when the result is neutral.

## 3. Graph databases are useful when relationships change eligibility

A graph is not compelling merely because it can draw nodes and arrows. In Relay, the useful question is whether the dependency path and procedure relationships change what the worker is allowed to do.

The incident can traverse checkout to inventory to warehouse. A procedure applies to a service only under particular conditions. Evidence supports or contradicts hypotheses. Those relationships are useful because they can affect action eligibility and explainability.

That also creates a design obligation: the interface must render the relationships returned by the database. A hardcoded graph can look convincing while hiding that the underlying state changed. The graph is only evidence when removing or changing a relationship changes the returned context and the allowed action.

## 4. Coordination requires conditional writes and fencing

Two workers reading the same open task can both believe they are responsible. Relay uses conditional graph writes for claims and a token to fence later writes. The integration tests run independent Python processes against FalkorDB and verify that only one claimant owns the task.

The important idea is not the token itself. It is that ownership is checked at every state-changing boundary. A worker that has lost its claim must not be able to append evidence, create a handoff, or finish an action.

This is also where I learned to be conservative around external effects. A request timeout does not prove that the HTTP action did not execute. Relay leaves an uncertain operation running rather than silently retrying it with a new operation ID.

## 5. Exactly-once behavior has a boundary

A graph database and an external service cannot form one atomic transaction without a broader coordination protocol. Relay reserves an operation in the sandbox before applying the effect and reuses the same receipt for a repeated operation ID. That prevents a straightforward duplicate execution.

The process can stop after an external effect and before the graph records the response. Relay handles that window through reconciliation using the original operation identity, preserving the receipt without dispatching the action again.

This distinction changed the product language I use. I do not claim exactly-once execution. I claim conservative duplicate prevention plus an explicit path toward reconciliation.

## 6. Safety must exist below the model

The model chooses from an allowlisted set of tools and must cite existing incident evidence. The application checks the task token, failed actions, procedure applicability, receipt identity, and independent health state before resolving the incident.

The model selects and explains a bounded action. FalkorDB remains the authority for ownership, evidence, procedure eligibility, and repeated-action guards.

The same principle applies to citations. Checking that an episode ID exists is not the same as proving that the episode justifies the action. A mature system needs action-specific evidence types, freshness, target matching, and deduplication.

## 7. Failure recovery is part of the product

The easiest demo path is a successful run. The harder and more valuable work is deciding what the user sees when:

- the database is temporarily unavailable;
- the browser loses a mutation response;
- the model returns malformed output;
- the worker lease expires during inference;
- the external service may have executed an action; or
- the final health check fails after the tool returned success.

A retry button is not a recovery design. The UI must reload authoritative state, preserve the incident identity, distinguish running from uncertain, and avoid dispatching a second effect just because the first response was lost.

## 8. A local demo and a production service are different products

Relay currently works best as a local, single-scenario application. FalkorDB, the sandbox, and Python worker subprocesses are stateful. That makes a static deployment platform a good home for the console but not for the entire runtime.

The production shape is a split deployment: Vercel serves the React interface, while a persistent backend host runs the API, FalkorDB, sandbox, and optional model provider. Authentication and tenant authorization are backend responsibilities; a tenant ID in a URL is not authentication.

Writing this boundary down was useful because it prevented a common deployment mistake: forcing a stateful worker system into serverless functions just because the frontend was easy to deploy there.

## 9. What I would build next

The highest-value next steps are not more frameworks. They are:

1. Make staged requests idempotent and validate state before side effects.
2. Add receipt lookup and a fenced reconciliation workflow for uncertain actions.
3. Render the actual graph response instead of a fixed scenario illustration.
4. Measure a history-sensitive scenario with paired memory and no-memory runs.
5. Add authentication, authorization, retention, tracing, and browser recovery before public multi-user use.
6. Deploy the console to Vercel while keeping the stateful runtime on a protected persistent host.

The central lesson is simple: durable memory is valuable when it changes what a successor can safely know and do. The database, workflow guards, evidence model, UI, and evaluation all have to make that change observable.
