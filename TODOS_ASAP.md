# Relay: TODOs ASAP

Updated: 2026-10-18

This is the working backlog for the next session. Keep the project narrow: durable incident memory, safe handoff, bounded repair, and independently verified recovery.

## Implemented and verified locally on October 18

- [x] Staged mutations replay without repeating completed effects; an early guard request dispatches no tool.
- [x] Tasks persist explicit workflow stages, and uncertain action delivery cannot be reclaimed automatically.
- [x] Lost responses reconcile by the original operation ID without re-execution.
- [x] Configuration and receipts use strict typed contracts, freshness checks, service/case/tool correlation, and independent health verification.
- [x] The console renders backend dependency paths, procedures, evidence, actions, receipts, worker PIDs, run IDs, selected episode IDs, and context hashes.
- [x] Successive console stages execute in distinct Python worker processes.
- [x] Cognee-derived retrieval is attributed, incident-scoped, size-bounded, persisted, and linked to source episodes with `CITES` edges.
- [x] A three-pair local-Mistral history ablation is stored at `artifacts/evaluation/mistral-history-ablation.json`; no proposed action was executed.
- [x] Final local checks: 36 tests, Ruff, and the React production build pass.

Still blocking a public submission: public repository and deployment URLs, API authentication/rate limits, a resettable public tenant, and the final recording. These require external hosting/account choices. The evaluation also found that history-enabled answers cited the failed receipt but omitted the current probe.

## Current Deployment Shape

- Vercel hosts the React/Vite console.
- A separate persistent backend host runs FastAPI, FalkorDB, the sandbox, and any model provider.
- `vercel.json` builds the frontend from `frontend/`.
- `VITE_RELAY_API` points the browser to the public HTTPS API.
- `RELAY_WEB_ORIGINS` restricts API CORS to the Vercel domain.
- FalkorDB and the sandbox must not be publicly exposed.

See `docs/deployment-vercel.md` before deploying.

## P0: Do Before Recording

### 1. Deploy a working public demo

- Deploy the frontend to Vercel.
- Deploy the API and stateful services to a persistent backend host.
- Confirm `/health` from outside the local machine.
- Run the complete deterministic flow from a clean browser.
- Add a resettable demo tenant or per-session demo incident.
- Keep model credentials and database credentials server-side.

### 2. Fix workflow replay safety

- Add an explicit persisted stage/state field.
- Add request IDs to mutating demo endpoints.
- Validate the stage before claiming or dispatching an action.
- Make completed stage requests return the stored result.
- Ensure guard-test-before-first-shift rejects without executing a tool.
- Release a claim only when failure is confirmed before action reservation.
- Preserve the case reference after transient API or database errors.

Suggested stages:

```text
created -> first_shift_running -> handoff_ready -> successor_running
         -> verifying -> resolved
                              \-> uncertain
```

### 3. Make the graph view truthful

- Render `dependency_paths` from the snapshot.
- Render actual `procedures` and their conditions.
- Render evidence links, hypothesis supersession, and action/result edges.
- Remove hardcoded service names and relationships from the primary graph.
- Display `unknown` when the backend has no evidence.
- Show the query/result behind the visual explanation in an expandable panel.

### 4. Make the handoff visibly real

- Use separate worker processes for the recorded flow.
- Show Worker A start and exit.
- Show Worker B start with a different process ID.
- Persist and display worker ID, run ID, process lifetime, selected episode IDs, and context hash.
- Make clear which facts were retrieved from FalkorDB and which are current observations.

### 5. Add one history-dependent evaluation scenario

Current configuration must be ambiguous enough that historical evidence changes the safe choice.

Compare identical runs:

- Same model and model settings.
- Same current observations.
- Same tools and action budget.
- With historical memory.
- Without historical memory.

Record for every run:

- Proposed tool.
- Executed tool.
- Whether the proposal repeated a failed action.
- Citation IDs and citation relevance.
- Recovery success.
- Latency and token usage.
- Errors and handoffs.

Do not present the database guard alone as proof that the model remembered.

## P1: Do Before Calling It Production-Ready

### 6. Add uncertain-operation reconciliation

- Preserve the original operation ID after a timeout.
- Query the sandbox receipt using that operation ID.
- Accept completion only when operation, case, tool, and receipt match.
- Add an explicit `uncertain` or `reconciling` state.
- Require an auditable operator decision for incomplete reservations.
- Never retry an uncertain external effect with a new operation ID.

### 7. Strengthen evidence and procedure contracts

- Use typed observations with service, observed value, expected value, source, version, and observation time.
- Reject missing, stale, malformed, or future-dated evidence.
- Validate stored procedure conditions instead of hardcoding the route rule.
- Bind the selected evidence and procedure version to the reserved action.
- Recheck eligibility at action reservation time.
- Distinguish tool execution success from service recovery success.

### 8. Improve citation validation

- Deduplicate citations.
- Require action-specific evidence types.
- Check target service, freshness, and validity.
- Link decision -> citation -> action -> result in the graph.
- Label current validation accurately: existing IDs are not automatically proof.

### 9. Add public API protection

- Authenticate callers before public multi-user exposure.
- Derive tenant scope from identity, not a URL or header alone.
- Add rate limiting and request size limits.
- Keep CORS limited to exact production origins.
- Add audit logging for reset, reconciliation, and action requests.

### 10. Make frontend recovery authoritative

- Preserve active case identity through errors.
- Reload the persisted snapshot after every mutation timeout or ambiguous response.
- Show `open`, `claimed`, `running`, `uncertain`, `done`, and `resolved` distinctly.
- Add a visible refresh/reconcile action.
- Show last connection check and last service observation separately.
- Test refresh, duplicate tabs, request cancellation, offline mode, and lost responses.

## Demo Script

Use a three-minute recording with a live backup:

1. Checkout is unhealthy; explain the handoff problem.
2. Worker A records the outage and attempts the wrong restart.
3. The failed receipt is persisted in FalkorDB.
4. Worker A exits.
5. Worker B starts independently.
6. Worker B retrieves the failed action, dependency path, and handoff evidence.
7. The bounded decision cites the retrieved evidence.
8. The graph guard rejects repeating the failed action.
9. Worker B executes the alternative repair.
10. An independent HTTP probe verifies recovery.
11. Show the operation receipt and final graph state.
12. State measured results and limitations honestly.

Use deterministic policy mode for the main recording if model latency is risky. Include a separate artifact showing the real local-model decision and label both modes.

## What Not To Do Yet

- Do not add another domain.
- Do not add Graphiti or MCP only for feature count.
- Do not claim general autonomous diagnosis.
- Do not claim exactly-once execution across FalkorDB and HTTP.
- Do not claim tenant authentication from tenant graph names.
- Do not turn a hardcoded diagram into claimed graph evidence.
- Do not spend the remaining build window on broad framework migration.

## Patterns To Borrow From The Winning Kit

Reference project: [Port + Bright Data + SigNoz Hackathon Kit](https://github.com/bgoconnor/port-brightdata-signoz-hackathon-kit).

- Keep one authoritative product specification. Treat this file and the implementation docs as the current contract; mark historical research separately.
- Define hard meanings for outcomes. For Relay, distinguish `resolved`, `not_resolved`, `uncertain`, `handed_off`, and `blocked`; do not treat a completed process as proof of recovery.
- Write the demo script before adding features. Build only what appears in a shot.
- Make the rejection path a first-class demo moment. Show an unsafe repeat being rejected and explain why.
- Maintain a deterministic fixture path that works without paid credentials or live providers.
- Keep fixtures separate from canonical runtime state. Demo seed data must never be presented as live operational memory.
- Add an evidence contract to every important run: input, selected context, query or tool, output, receipt, timestamp, and outcome.
- Instrument the incident path with run IDs, step names, row counts, latency, and errors so one trace can explain the result.
- Create smoke tests for clean setup, health, complete flow, failure injection, and recovery.
- Use explicit checkpoints: public URL, first successful run, complete video, then hard freeze. Stop adding features after the freeze.
- Prefer boring, visible reliability over optional integrations. A verified narrow feature beats an unverified framework list.

## Frontend Direction: Nexus-Inspired, Professional Relay

Borrow Nexus's information architecture and graph visibility, not its pixel-art office aesthetic. Relay should feel like a calm incident operations console: precise, restrained, readable, and trustworthy.

### Borrow These Product Ideas

- **Live run trace:** show the current worker, run ID, step, elapsed time, tool, and state as the incident progresses.
- **Graph topology view:** render the actual dependency path and highlight the affected service, traversed dependencies, selected procedure, and action target.
- **Current versus superseded knowledge:** make current hypotheses and replaced hypotheses visually distinct, with validity timestamps and contradiction links.
- **Evidence drawer:** selecting an event should reveal the source episode, payload, query/result, freshness, citations, and receipt without leaving the main incident view.
- **Operational status bar:** show API connection, FalkorDB availability, sandbox availability, provider mode, last refresh, and whether the state is live, stale, running, or uncertain.
- **Run history:** allow the operator to open the latest run and compare the decision, citations, action, and verification outcome.
- **Visible graph changes:** changing a dependency or procedure should visibly change the topology and eligibility explanation.
- **Degraded mode labels:** clearly distinguish deterministic policy, local model, saved replay, unavailable provider, and uncertain external operation.

### Keep The Visual Language Professional

- No 8-bit characters, pixel-art rooms, playful avatars, or game-like animation.
- Use a restrained light interface with charcoal text, off-white surfaces, slate borders, and a small semantic status palette.
- Reserve color for meaning: green for independently verified, amber for running or stale, red for failed or blocked, blue for selected evidence, and neutral gray for historical context.
- Use one expressive display face for major headings and a highly readable sans-serif for operational content; avoid default dashboard typography.
- Keep the main incident page unframed and information-dense. Use cards only for repeated evidence items, receipts, and focused tools.
- Prefer compact tables, timelines, drawers, tabs, and split panes over decorative dashboards.
- Keep graph labels readable at normal zoom and provide a textual relationship list for accessibility.
- Use motion only for step arrival, graph updates, and status transitions. Respect `prefers-reduced-motion`.
- Make unknown state explicit. Never imply that a service is healthy, a citation is relevant, or a relationship exists only because a visual default was rendered.

### Recommended Incident Console Layout

```text
Header: incident status | owner | worker | run ID | provider | connection

Left:    chronological evidence and handoff timeline
Center:  current decision, citations, action state, and receipt
Right:   dependency graph, procedure eligibility, current/superseded beliefs

Bottom:  expandable run trace with Cypher, rows, latency, context hash, and errors
```

The first viewport should answer five questions without narration:

1. What is broken?
2. Who owns the incident now?
3. What did the previous worker try?
4. What evidence changed the successor's decision?
5. How was recovery independently verified?

### Nexus Observations To Preserve In The Backlog

- Its graph is a product surface, not only a backend implementation. Relay should make FalkorDB relationships visible in the primary workflow.
- Its live event stream makes a fixed sequence feel like an operating system. Relay can achieve the same effect with polling first, then SSE if time allows.
- Its decision lineage and stale-knowledge views are valuable patterns for Relay's hypothesis supersession and evidence freshness.
- Its run history and debug views make claims inspectable. Relay should expose a focused version of this rather than a generic debug page.
- Its deployment and landing experience reduce demo friction. Relay needs a clear public URL, health indicator, resettable demo state, and first-run instructions.
- Its visual spectacle is memorable, but Relay's visual identity should communicate operational trust rather than playfulness.

## Integration Strategy: One Practical Incident Pipeline

Do not ingest every company system. Add a small source-to-memory pipeline that makes a real operational handoff possible.

### Recommended Practical Use Case

**Deployment incident handoff:** a deployment changes a service dependency, checkout health fails, the first agent investigates and hands off, and a successor uses the combined source history to choose and verify the repair.

```text
GitHub PR / deploy event
    +
Alert or health observation
    +
Service topology and runbook
    v
FalkorDB incident graph
    v
Scout -> Planner -> Successor/Scribe
    v
bounded action -> receipt -> independent verification
```

The value is not merely answering a question. The system should show that source history changes what the next agent knows, who owns the work, which action is eligible, and how recovery is verified.

### Source Integrations By Priority

#### P0: Deterministic source adapters

- JSONL or webhook event ingestion for deploys, alerts, health checks, and handoffs.
- Synthetic GitHub-style pull request and commit events with repository, service, author, changed files, and deployment version.
- Runbook/procedure records containing target service, preconditions, allowed tools, and expected verification.
- Current service topology and ownership records.

These should work offline and require no credentials. Use the same event shape for fixtures and live webhook requests so the demo path and integration path share code.

#### P1: One real external source

Choose only one:

- **GitHub public repository:** ingest release/PR metadata and link changed paths to services.
- **OpenTelemetry webhook or collector:** ingest a deployment span, error span, and health signal.
- **Sentry-style alert webhook:** ingest a synthetic alert payload and preserve issue ID, service, release, and timestamp.

GitHub is the easiest public demo source. OpenTelemetry is the strongest observability story. Sentry is the simplest alert-to-incident story. Do not implement all three during the hackathon.

#### P2: Optional enrichment

- Slack or Discord incident messages, only with explicit redaction and consent.
- PagerDuty or Opsgenie ownership and escalation events.
- Service catalog metadata such as team, tier, and on-call owner.
- Historical runbook outcomes as procedural memory.

These are production integrations, not required for the competition proof.

### Graph Mapping

Add source provenance without replacing the existing incident model:

```text
SourceEvent -[:ABOUT]-> Service
SourceEvent -[:TRIGGERED]-> Incident
PullRequest -[:CHANGED]-> Service
Deployment -[:DEPLOYED]-> Service
Deployment -[:INTRODUCED]-> Configuration
Alert -[:OBSERVED]-> Service
Runbook -[:APPLIES_TO]-> Service
Episode -[:DERIVED_FROM]-> SourceEvent
Decision -[:CITES]-> Episode
Action -[:VERIFIED_BY]-> HealthReceipt
```

Every ingested event should retain:

- Source and external ID
- Event time and ingestion time
- Tenant and service scope
- Source URL or safe reference
- Payload hash
- Schema version
- Whether the fact is current, superseded, or uncertain

Ingestion must be idempotent on `(source, external_id)` and reject cross-tenant references.

### Agent Coordination Story

Use three clearly bounded roles:

1. **Scout:** correlates the alert, deployment, changed service, dependency path, and owner; creates the task.
2. **Planner:** claims the task, retrieves failed attempts and applicable procedures, and proposes one allowlisted action with citations.
3. **Successor/Scribe:** continues after handoff, validates the action against current evidence, executes it with an operation ID, stores the receipt, and performs independent verification.

The roles may be implemented as separate Python workers. The important proof is that the successor reads durable graph state rather than receiving an invisible copied prompt.

### Integration Contract

Add an ingestion endpoint or CLI command with this shape:

```json
{
  "source": "github",
  "external_id": "repo:commit:abc123",
  "event_type": "deployment",
  "tenant": "acme",
  "service": "inventory",
  "occurred_at": "2026-10-18T10:00:00Z",
  "payload": {},
  "source_url": "https://github.com/example/repo/commit/abc123"
}
```

The adapter normalizes this into graph nodes and provenance episodes. The core runner must consume the normalized graph contract, not provider-specific payloads.

### What To Demonstrate

- Ingest a deployment event.
- Ingest or generate an alert against the affected service.
- Show the dependency and ownership path in the graph.
- Let Worker A investigate and record a failed attempt.
- End Worker A and start Worker B.
- Let Worker B retrieve the deployment, alert, failed attempt, and runbook.
- Reject a repeated unsafe action.
- Execute the bounded alternative.
- Verify recovery and show the source-to-decision-to-receipt chain.

## 70-80% Track Coverage Roadmap

Do not implement every possible memory feature. Reach broad coverage through one coherent incident lifecycle that exercises most capabilities end to end.

### Coverage Targets

| Capability | Current | Target addition |
|---|---|---|
| Episodic memory | Strong | Add source provenance and retrieval evaluation. |
| Semantic memory | Partial | Add normalized facts, validity intervals, supersession, and cross-incident retrieval. |
| Procedural memory | Partial | Store reusable procedures, outcomes, preconditions, and confidence. |
| Conversation history | Limited | Persist conversations, turns, handoff summaries, and episode references. |
| Shared state/handoffs | Strong | Add worker sessions, run IDs, and visible handoff receipts. |
| Concurrency | Partial | Add same-task races, stale leases, snapshot consistency, and load tests. |
| Tenant separation | Storage strong, auth absent | Add authenticated tenant scope and authorization tests. |
| Connected reasoning | Narrow | Add deployment, alert, ownership, topology, and runbook relationships. |
| Explainability | Partial | Persist source -> episode -> decision -> action -> receipt -> verification. |

### Build Order

#### 1. Normalize the incident graph

Add durable entities for `Conversation`, `ConversationTurn`, `WorkerSession`, `SourceEvent`, `Deployment`, `Alert`, `Fact`, `Procedure`, `Decision`, `Receipt`, and `Verification` alongside the existing incident model.

Every source event and fact needs tenant, source ID, event time, ingestion time, validity, and schema version. Ingestion must be idempotent on `(source, external_id)` and reject cross-tenant references.

Use relationships such as:

```text
SourceEvent -> Incident -> Task -> WorkerSession
Deployment -> Service
Alert -> Service
Service -> DEPENDS_ON -> Service
Procedure -> APPLIES_TO -> Service
Episode -> DERIVED_FROM -> SourceEvent
Episode -> SUPPORTS/CONTRADICTS -> Hypothesis
Hypothesis -> SUPERSEDES -> Hypothesis
Decision -> CITES -> Episode
Action -> HAS_RESULT -> Receipt -> VERIFIED_BY -> Verification
```

#### 2. Add a bounded multi-agent lifecycle

- **Scout:** correlates alert, deployment, topology, and ownership evidence.
- **Planner:** claims the task, retrieves semantic/procedural/episodic context, and proposes one allowlisted action.
- **Successor/Scribe:** reads the durable handoff, validates the action, executes it, records the receipt, and verifies recovery.

Each worker needs a durable session, run ID, selected context, handoff summary, and exit status. Application guards remain authoritative over model output.

#### 3. Complete the memory types

Semantic memory should store facts such as `inventory DEPENDS_ON warehouse` and `inventory ROUTE_IS /stock` with `valid_from`, `valid_until`, `observed_at`, and source episode IDs. Retrieve current facts separately from historical facts.

Procedural memory should store triggers, preconditions, targets, tool sequences, successful and failed outcomes, and confidence. A procedure is eligible only when its current preconditions match.

Conversation memory should persist user turns and agent turns as episodes linked to cited facts, decisions, and actions. A new worker must be able to reopen the conversation without receiving an invisible copied prompt.

#### 4. Add the connected-data layer

Use the deployment incident to cover Track 01:

- Traverse dependencies to calculate blast radius.
- Resolve service ownership and on-call team.
- Link a deployment or pull request to the affected service.
- Find the latest applicable decision or runbook.
- Select a repair based on graph relationships and current evidence.
- Explain the full path in the UI and persisted trace.

#### 5. Prove coordination and isolation

Add executable tests for same-task claim contention, concurrent action starts, stale writes after handoff, slow model completion after lease expiry, snapshot reads during writes, cross-tenant citations, authenticated tenant access, and p50/p95 latency as worker counts increase.

Report correctness and throughput separately. A small race test is not a production benchmark.

### Hackathon Definition Of Done

One recorded scenario should demonstrate:

1. A source event creates or updates an incident.
2. Graph traversal identifies affected services and owners.
3. Worker A stores an observation, conversation turn, hypothesis, and failed action.
4. Worker B claims the task through a durable handoff.
5. Retrieval returns episodic, semantic, and procedural evidence.
6. The graph blocks an unsafe repeated action.
7. The successor executes one bounded repair.
8. A receipt and independent verification close the incident.
9. The UI shows the source-to-memory-to-action chain.
10. Tests prove tenant boundaries, stale-worker rejection, and same-task claim safety.

This provides broad Track 02 coverage and a credible Track 01 connected-reasoning story without building unrelated integrations.

### What Not To Build Yet

- A general Slack/Linear/GitHub/Datadog connector suite.
- Full OAuth flows for private accounts.
- A generic document chatbot.
- Embedding search before lexical/graph retrieval is evaluated.
- Provider-specific graph models that bypass the normalized event contract.

The winning Track 02 claim should be: **Relay turns heterogeneous incident evidence into durable, scoped memory that lets a fresh worker continue safely and explainably.**

### What Not To Copy Blindly

- A broad feature catalog can dilute Relay's stronger incident-recovery story.
- Keyword-based benchmark accuracy is useful for a smoke test, not proof of general intelligence.
- A concurrency test with separate tasks does not prove same-task claim contention.
- An ephemeral single-container deployment is suitable for a sample-data demo, not durable production memory.
- Fixed agent order should be labeled as orchestration, not autonomous planning.

## Submission Checklist

- [ ] Public source repository URL works signed out.
- [ ] Vercel production URL works.
- [ ] Backend HTTPS URL works.
- [ ] Clean-browser deterministic demo works.
- [ ] Video shows a real handoff, not only a state transition.
- [x] Model/policy modes are labeled.
- [x] AI assistance and synthetic data are disclosed.
- [x] Track 02 claim is narrow and defensible.
- [x] Setup uses locked dependencies and documents Node/Python versions.
- [x] Evaluation artifact includes raw runs, not only a headline percentage.
- [x] Limitations mention authentication, sandbox isolation, and uncertain operations.
