# Relay: independent judge-style review

Reviewed October 17, 2026. This is an unofficial assessment of the current workspace, not an organizer's decision or a prediction of the other entries. Application code was not changed during the review.

**Verdict: a credible Track 02 prototype, but not submission-ready and not yet supported by winning-level evidence.** The operational memory and coordination are real. The weakest parts are the proof that historical memory helps the agent, the accuracy of the visible graph/provenance claims, interrupted-workflow recovery, and the submission package. More frameworks will not resolve those weaknesses.

## Evidence and limits

Reviewed backend, Cypher, sandbox, CLI, Graphiti bridge, React/TypeScript interface, configuration, tests, and project/research documentation. Rechecked the official rules and track page. Ran:

| Check | Result and interpretation |
| --- | --- |
| Default pytest | 8 passed, 14 skipped. This command alone does not test the operational graph. |
| `RELAY_INTEGRATION=1 .venv/bin/pytest -q` | 22 passed in 3.98 seconds against local FalkorDB and sandbox. |
| Ruff | Passed. |
| Frontend production build | Passed. This is not a browser behavior test. |
| Nine targeted fault probes | Reproduced the defects below using real disposable graphs and mocked sandbox/model responses. |
| Graphiti first-episode ingestion probe | `NodeNotFoundError` with installed Graphiti 0.30.2; zero inference, embedding, or reranking calls. |
| Fresh local Mistral workflow | Resolved the real synthetic incident in 32.04 seconds overall; model runtime reported 31.24 seconds, 1,946 prompt tokens and 136 output tokens. One sample, not an accuracy benchmark. |
| Repository check | `git status` reports that this folder is not a Git repository. No public repository link was found in the reviewed project documentation. |

See [recorded probe results](2026-10-17-probe-results.json). Unique audit graphs were deleted. Existing test/demo graphs were not deleted; synthetic sandbox rows created by integration tests remain. No cloud model calls or paid services were used. A new browser walkthrough, clean-checkout installation, throughput benchmark, and database restart were not performed. Earlier restart/browser observations remain historical evidence in [verification.md](../verification.md), not new findings of this audit.

## Rules and eligibility

The event window is October 15, 12:01 AM–October 18, 11:59 PM IST, 2026. FalkorDB must power central functionality. Submission requires public source, setup/model documentation, essential queries, a working video, a deployment or complete local instructions, and named tracks. AI assistance must be disclosed; participant understanding and meaningful contribution matter. Use permitted data and respect the event coding boundary. [Official rules, accessed October 17](https://www.wemakedevs.org/hackathons/falkordb/rules).

| Requirement | Current evidence | Assessment |
| --- | --- | --- |
| Central FalkorDB use | Operational state, ownership, history and eligibility queries live in FalkorDB; database failure has no fallback. | Strong. The SQLite sandbox receipt store does not undermine this. |
| Public source | No Git repository here or documented public URL. | Submission blocker until accessible source is provided. A repository elsewhere remains possible but unverified. |
| Setup/model/queries | README, implementation model, executable parameterized Cypher, lockfiles. | Substantive; clean-machine setup remains unverified. |
| Working video | Documentation still describes it as next work; no linked video found. | Submission blocker if still missing at deadline. |
| Deployment/local setup | Local path exists; frontend prerequisites and configuration need tightening. | Local delivery is viable; public hosting is not necessary to finish this entry. |
| Named track | README names Track 02; Track 01 is only a secondary opportunity. | Explicitly match the final submission form to the actual demonstrated scope. |
| Data/AI disclosure | Synthetic fixtures and Codex disclosure are present. | Good. Participant understanding cannot be established by automated tests. |
| Build provenance | README reports implementation began October 15; no local commit history. | Not independently verified. Absence of Git is not evidence of a timing violation. Preserve truthful history from now on. |

The rules research document still says to keep the workspace research-only and has an entirely unticked submission checklist. Preserve its historical date but add a current status rather than leaving contradictory instructions.

## How I would judge the track fit

Track 02 emphasizes persistent, evolving memory, handoffs, concurrency and tenant separation, including episodic, semantic and procedural memory and conversation history. These are published focus areas, not a verified weighted rubric or a requirement to implement every item. Track 01 emphasizes connected reasoning, graph-backed actions and explainability. [Official tracks, accessed October 17](https://www.wemakedevs.org/hackathons/falkordb).

| Dimension | Judgment |
| --- | --- |
| Episodic memory | Strongest part: persisted observations, attempts, results, claims and handoffs. |
| Semantic memory | Limited but real: fixed service topology and application-managed hypotheses. It does not yet demonstrate generalized knowledge extraction or retrieval. |
| Procedural memory | A seeded procedure is retrieved from the graph. Its precondition is not actually evaluated as stored; nothing learns a procedure from outcomes. |
| Cross-session continuity | Real in the CLI, which starts separate processes. The browser workflow does not itself establish that process boundary. |
| Coordination | Conditional writes, fencing and conservative uncertain-operation handling are good. Only small-scale contention is demonstrated, with no operational recovery path from uncertainty. |
| Tenant separation | Separate graph namespaces are tested. This is storage scoping, not authenticated user isolation. |
| Conversation memory | Incident episodes exist; general conversation persistence is not implemented. Acceptable scope if described accurately. |
| Model contribution | One bounded successor tool decision. Agent A, inspection and diagnosis correction are application logic. Default policy mode makes no model call. |
| Differentiation | The restart/handoff story is useful, but the current easy fault and fixed topology make it look close to a scripted orchestration demo. |
| Track 01 | Plausible secondary fit, weaker than Track 02. Actual traversals exist, but a single known path and two fixed actions do not demonstrate broad graph reasoning. |

**I would credit this as a working graph-backed system. I would not award Track 02 on the current evidence alone.** A competitor demonstrating a necessary historical fact, observable fresh-process retrieval, correct changing facts, and measured outcomes would have a clearer case.

## Findings, ordered by submission impact

Priority meanings: **P0** before recording/submitting; **P1** important correctness or evidence work; **P2** defer unless promoting the affected capability. These are project priorities, not security severity ratings. “Reproduced” means observed in this review; “source-confirmed” means directly visible in code; “untested risk” is deliberately not claimed as a reproduced failure.

### F01 — P0: the claimed memory advantage is not demonstrated

**Source-confirmed evaluation gap.** [Runner](../../src/relay/runner.py), lines 87–130, inspects fresh configuration, programmatically supplies the corrected diagnosis, then asks the model to select a tool. [Sandbox](../../sandbox/server.py), lines 83–91, supplies both the wrong route and the expected route. A successor without historical memory could infer the same repair. The new live Mistral sample cited the fresh configuration, not the predecessor's failed attempt.

Persistence and guard enforcement are valuable, but neither establishes improved model reasoning. The guard test deliberately requests a forbidden action; it is not evidence that the model independently avoided it. There is no paired memory/no-memory artifact.

**Improve:** add one controlled variant where historical outcomes disambiguate two plausible actions. Compare identical models, current observations, tools and budgets with and without historical context. Separate proposed repeats from executed repeats. Preserve neutral and failed results. Do not use the current `resume` prerequisite as a baseline: it explicitly rejects missing failed-restart history, mechanically forcing that baseline to fail.

### F02 — P0: the “live” graph is a hardcoded illustration

**Source-confirmed.** [Frontend](../../frontend/src/main.tsx), lines 100–119 and 289, draws fixed services, edges, a procedure and health labels. It does not render `dependency_paths`, `procedures` or `evidence_links`. Only two activation flags use current data. Removing a dependency from the database would not remove its displayed path. “Route mismatch” remains after recovery; “warehouse healthy” is not derived from a displayed probe.

[README](../../README.md), line 72, overstates that dependency paths are read into the interface from the current snapshot. This does **not** make FalkorDB decorative in the backend, but it undermines the judge's trust in the evidence view.

**Improve:** render returned nodes/relationships and their actual state, expose the supporting query/result, and show unknown when evidence is absent. Until implemented, label the picture a scenario diagram. Never invent provenance edges to make a visual look connected.

### F03 — P0: browser handoff is not a fresh-process demonstration

**Source-confirmed boundary.** [API](../../src/relay/api.py), lines 86–98, directly calls both runner methods inside the API service. [CLI](../../src/relay/cli.py), lines 48–94, genuinely starts separate processes; the integration test also verifies this. Reconstructing a Runner object is not terminating the previous agent process.

**Improve:** either use the CLI process separation visibly in the recording, or launch independently identifiable workers from the console. Persist run/session IDs, process start/exit and a retrieval manifest showing which graph facts the successor actually received. Do not claim the current browser flow proves process death. An earlier description of the browser demo as a separate successor process was too strong.

### F04 — P0: replaying stages mutates state before rejecting the request

**Reproduced.** [Runner](../../src/relay/runner.py), lines 54–85:

- Replaying a successful first shift returns HTTP 409, leaves the task claimed and creates a second current hypothesis. Only one restart was dispatched; the repeat-action guard worked, but the workflow was damaged before it fired.
- Calling the guard endpoint before the first shift dispatches a restart, returns HTTP 500 and leaves the task claimed. A guard demonstration should reject the invalid stage before executing anything.
- A sandbox connection failure immediately after claiming the first shift leaves the claim held despite no tool having been started.

Lost responses, a refresh, two browser tabs or manual API calls can trigger these paths. A five-minute claim timeout is particularly disruptive in a short judging session.

**Improve:** explicit stage transitions and request idempotency, validated before side effects; repeat requests should return the prior outcome. Release ownership on confirmed pre-dispatch failures. Never release merely because delivery timed out after an action was reserved. Add regression cases for both boundaries.

### F05 — P0: repair preconditions accept missing evidence and ignore stored policy

**Reproduced.** [Runner](../../src/relay/runner.py), lines 38–47, treats a configuration payload `{}` as a mismatch because missing `route` is unequal to `/stock`. The restore tool was dispatched. Changing the graph procedure's `precondition` to require manual approval also did not block dispatch: the runner checks the procedure name and a hardcoded route rule, not the stored precondition or target.

**Improve:** typed observations containing service, observed/expected values, source, version and observation time; reject missing/ambiguous/stale evidence. Use structured supported procedure conditions and validate the target. Bind the validated evidence/procedure version to the action and recheck eligibility at reservation time. Do not execute arbitrary natural-language preconditions as code.

### F06 — P0: submission proof and reproducibility are unfinished

**Observed documentation/workspace gap.** Public source and video are not evidenced. README omits Node prerequisites and API/frontend ports from its requirements. It installs optional Graphiti by default and places an optional Ollama run before the API launch, increasing first-run friction. Browser Gemini requires environment variables in the API process; the documented `.env` example loads them only for the CLI. `npm run preview` normally serves a different origin from the two origins permitted by API CORS.

**Improve:** create the actual accessible source package, give a minimal deterministic setup plus clearly separate optional model instructions, use the frontend lockfile with `npm ci`, document the tested Node version, and verify from a clean directory. Record a working model run and the limitations. Present the implemented graph model prominently. No public deployment is needed to solve this particular gap.

### F07 — P1: uncertain tool outcomes stop duplicate execution but strand the workflow

**Source-confirmed; existing test covers the blocked state.** [Runner](../../src/relay/runner.py), lines 48–52, deliberately leaves a started action `running` on interruption. [Queries](../../src/relay/queries.py), lines 81–104, prevent reclaiming it. This is the correct conservative direction. However, there is no supported reconciliation operation in the API/CLI/UI.

A tool can finish and its durable sandbox receipt can exist while FalkorDB still says `running`. A new successor cannot claim the incident. If the sandbox reserved an operation but crashed before saving its receipt, retrying returns uncertainty forever. The current interface offers no useful next step.

**Improve:** an explicit uncertain/reconciling state, receipt lookup by the original operation ID, and fenced completion from a matching durable receipt. For incomplete reservations, require an auditable operator decision based on observed state. Never silently generate a new operation ID or claim exactly-once execution across the database and HTTP boundary.

### F08 — P1: persistence accepts contradictory health and mismatched receipts

**Reproduced at the trusted Python library boundary.** [Memory](../../src/relay/memory.py), lines 106–121, and [RESOLVE](../../src/relay/queries.py), lines 106–113:

- An episode named `health_verified` with `healthy: false` can resolve an incident.
- A completion receipt with the wrong operation ID and wrong tool but `healthy: true` marks an action successful.

The normal runner currently creates verified-health episodes only after a true probe, and public HTTP routes do not directly expose these append/finish methods. This is not a demonstrated unauthenticated remote exploit. It is a weak invariant for a system intended to accept multiple agent writers and future tool adapters.

**Improve:** typed probe/receipt contracts, operation/case/tool correlation, trusted producer identity, freshness and post-action linkage. A health episode's string label should not be sufficient proof. Distinguish successful tool execution from successful incident recovery.

### F09 — P1: citation validation proves existence, not justification

**Reproduced.** [Models](../../src/relay/models.py), lines 77–79, accepts any episode IDs in the incident. A model response citing the same task-claim episode twice as justification for a route repair was accepted. [Frontend](../../frontend/src/main.tsx), lines 155–165 and 221–224, labels output validated and counts citation entries as “Valid citations.”

**Improve:** immediately label these as references found/schema validated. Deduplicate, link citations to their episodes, and validate action-specific evidence type, target and freshness. Treat logical support as a separate evaluation criterion; schema validation cannot establish it. Persist decision-to-evidence and action-to-decision links if claiming a traversable explanation chain.

### F10 — P1: repaired faults remain “valid now,” and later decisions can be hidden

**Reproduced fault belief; source-confirmed decision display.** Even after real Mistral recovery, the current hypothesis remains “Inventory points to an invalid warehouse route.” [Frontend](../../frontend/src/main.tsx), lines 122–129, calls it “valid now.” A confirmed historical root cause and a currently broken configuration are different facts.

DecisionCard uses `.find`, so an earlier handoff or rejected decision remains displayed after a later successful decision. MiniGraph uses the same first-decision selection. Citation counts aggregate all decisions while the card displays the first one.

**Improve:** close or reclassify the active fault on verified repair while retaining the diagnosis as historical cause. Show the latest decision by default, with explicit history and attempt-specific metrics. Define whether concurrent hypotheses are alternative candidates or one authoritative fact; do not mix those semantics.

### F11 — P1: frontend errors can lose the active case and leave stale controls

**Source-confirmed; browser fault injection not performed.** [Frontend](../../frontend/src/main.tsx), lines 183–216, deletes the saved case reference on any restore error, including a temporary database outage. After a mutating request fails, it displays an error but does not reload authoritative state. The server may already have completed or partially completed that stage.

There is no polling/event stream, request timeout, active-case loader or reconciliation control. Connection status is checked once. Memory freshness updates only when React renders and uses the newest episode, which may be a claim rather than fresh service evidence. Stage calculation does not adequately represent running, leased or uncertain operations.

**Improve:** preserve case identity on transient failures, provide retry/read-only refresh and case reopening, reload after mutations/errors, and render server task states explicitly. Show last-checked connection status and last-observed service health separately. Cancellation of a browser request must not imply that server work was cancelled.

### F12 — P1 if advertised, otherwise P2: Graphiti ingestion is broken

**Reproduced without cloud calls.** [Bridge](../../src/relay/graphiti_bridge.py), lines 79–98, first confirms an episode UUID is absent and then passes that UUID to `add_episode`. In installed Graphiti 0.30.2, a supplied UUID selects an existing `EpisodicNode`; a new UUID raises `NodeNotFoundError`. The bridge therefore fails on its first new episode before extraction. The driver/index probe never exercises this behavior.

Primary implementation evidence: installed `graphiti_core/graphiti.py`, the `add_episode` branch around line 1158, and `graphiti_core/nodes.py`, `EpisodicNode.get_by_uuid` around line 362. The audit called the bridge against a new graph with inference, embeddings and reranking blocked; all call counts remained zero.

**Improve:** adapt to the installed creation contract and retain an explicit source-to-Graphiti identity/completion mapping; test first import, repeat import and interruption. Merely pre-creating a node would conflict with the bridge's current “exists means completed” skip rule. Then test extraction, contradictions and retrieval. The operational runner does not consume this optional semantic graph, so fixing import alone will not improve the core demo. Defer it rather than advertise a working semantic integration prematurely.

### F13 — P1 for broad claims: graph snapshots and temporal semantics are incomplete

**Source-confirmed design limits; race/scale effects unbenchmarked.** [Memory.snapshot](../../src/relay/memory.py), lines 123–178, makes several separate reads. A concurrent writer can produce a snapshot whose incident/task fields precede its later action/episode fields. There is no revision token or consistency check. Timestamps and lease checks use client wall clocks. Episodes are unbounded; the complete snapshot is sent to the model despite a finite local context window.

The core has no explicit index setup. Dependency traversal is bounded to four hops but not result count, so branching paths can expand. Snapshot provenance exports support/contradiction edges but not the complete action/result, decision/citation and supersession chain. Old observations have no separate observation-vs-ingestion time or validity policy.

**Improve:** coherent snapshot/revision handling, context selection and size limits, indexes appropriate to measured queries, stable event ordering, and explicit current/historical retrieval. Do not claim high concurrency or long-term memory scaling from the eight-contender test.

### F14 — P1 before multi-user exposure; P2 for this local demo: isolation has a narrow boundary

**Source-confirmed and already partially disclosed.** Tenant names select graphs; they do not authorize access. Any caller of this local API can request a known tenant's incident or claim its available task. Hashing names and CORS do not authenticate users. Loopback bindings are a useful current boundary.

The sandbox stores separate case configurations but uses one inventory subprocess and a global mutation lock. One case's restart can disrupt another case's health probe. A failed probe caused by that disruption can permanently blacklist an otherwise useful tool for the incident.

**Improve:** keep the submitted demo explicitly local and serial. Before public multi-user use, derive tenant scope from authenticated identity and test authorization, rate limits and credential handling. Before concurrent sandbox claims, isolate runtime effects or explicitly model their shared blast radius. Do not spend the remaining build window pretending this is production infrastructure.

### F15 — P1/P2: several generalization and usability limits are not covered

**Source-confirmed limits / untested outcomes.** A failed tool name is blocked for the entire incident even when configuration or prerequisites later change. New incidents always receive the same topology. General incident creation does not create a sandbox case, so demo endpoints are not interchangeable with the generic API. Initialization commits the graph before sandbox creation; failure leaves an orphan incident whose identity may not reach the UI.

Model input has no retrieval budget; Gemini empty/blocked candidate responses and transport failures are not mapped into useful typed user errors. There is no provider-readiness endpoint. Graphiti synchronization has no cross-process lock, and semantic current-fact filtering remains unverified. Sandbox receipts and test cases accumulate without retention. The frontend has no behavior tests, uses small 7–10px evidence text, and removes the provider select's outline without adding a custom focus indication.

**Improve:** prioritize explicit error/recovery states, readable evidence, and a truthful narrow scope. Version failed attempts by relevant context before permitting retries. Add only the scenario variations needed to test the memory thesis. Broader retention, topology management, provider adapters and access controls can remain documented limitations.

## Where execution can fail

| Failure window | Current consequence | Required behavior / evidence |
| --- | --- | --- |
| Graph created; sandbox creation fails | Orphan graph incident; start request errors. | Persist initialization status and return recoverable identity; retry same sandbox case safely. |
| Task claimed; observation fetch fails | Claim remains held until expiry. | Release only when no action could have been dispatched; retain an error episode. |
| First shift completed; HTTP response lost | UI can retry the old stage and corrupt workflow state. | Request identity and persisted stage outcome; reload authoritative state. |
| Model returns malformed output, times out or hits quota | Existing model exception path hands off; UI error may be generic/stale. | No tool dispatch, persisted provider/error category and usable retry. |
| Model reasoning exceeds lease or another worker reclaims | Late writes should fail fencing; handoff error may mask original failure. | Exercise slow inference, expiry and stale-owner rejection; no unowned action. |
| Action reserved; process dies before HTTP send | Task stays running even if nothing executed. | Reconcile using operation state; do not assume non-execution from missing response. |
| Sandbox reserves operation; dies before effect | Incomplete receipt reservation refuses replay. | Surface uncertainty; operator-supported resolution without silent re-execution. |
| External effect occurs; receipt not saved | State changed but no durable completion proof. | Inspect actual state, preserve uncertainty and audit any recovery decision. |
| Receipt saved; reply lost | Sandbox can return matching cached receipt, but runner offers no reconciliation command. | Query/reuse original operation identity; finalize graph under fencing. |
| Graph finish succeeds; final probe fails | Task may remain claimed, or repair may be recorded failed from transient health. | Separate execution outcome and service outcome; bounded verification policy. |
| Health verified; graph resolution fails | Healthy service with open incident. | Replay a fresh/correlated verification safely, without repeating remediation. |
| Graph resolves; UI response lost | Browser can show stale stage and attempt another request. | Read persisted completion; idempotent stage response. |
| Database restarts during reads/writes | Errors; intermediate multi-query snapshot or lost acknowledgment possible. | Durable-state verification and idempotent commands, not fallback in-memory truth. |
| Another tenant restarts shared inventory | Probe interruption in this case despite separate graph namespaces. | Serial demo boundary or isolated runtime effects. |
| History grows beyond model context | Relevant failure/validity evidence may be truncated or inference may fail. | Retrieval budget and explicit selected/omitted evidence, tested at increasing sizes. |

## Coverage matrix

This is a scoped checklist, not a claim to enumerate every possible failure. **Pass** means demonstrated by the current tests/review; **Defect** means reproduced or directly source-confirmed as described above; **Partial** means a narrower behavior is verified; **Open** means it needs a test. P0 applies before the final recording, P1 before making the associated reliability claim, and P2 to optional/generalized scope.

| ID | Case and required assertion | Current status | Priority |
| --- | --- | --- | --- |
| S01 | Two CLI processes recover the same incident with no shared Python objects. | Pass, policy integration test. | P0 |
| S02 | Real local model chooses, cites and recovers without hidden fallback. | Pass, one review sample. | P0 |
| S03 | Browser demo visibly proves distinct worker lifecycle and retrieval. | Defect in claimed proof; same API process. | P0 |
| S04 | Database restart preserves incident, attempts and beliefs exactly. | Partial: earlier verification record, not rerun here. | P1 |
| S05 | Duplicate first-shift request returns prior result without extra writes. | Defect, reproduced. | P0 |
| S06 | Guard request before failed attempt has no tool side effect. | Defect, reproduced. | P0 |
| S07 | Duplicate resume, two tabs and post-resolution requests are safe/idempotent. | Open; claims prevent some overlap, not full replay semantics. | P0 |
| S08 | Initialization failure preserves recoverable identity. | Defect in current flow; outage injection open. | P1 |
| M01 | Failed attempt is retrievable after handoff. | Pass. | P0 |
| M02 | Supersession keeps old belief and its evidence. | Pass, simple single-writer case. | P0 |
| M03 | Verified repair closes present-tense fault validity. | Defect, reproduced. | P1 |
| M04 | Empty/malformed configuration cannot authorize repair. | Defect for empty payload; malformed types open. | P0 |
| M05 | Stale, wrong-service or future-dated evidence cannot authorize repair. | Open; no robust validation contract. | P1 |
| M06 | Procedure precondition/target changes affect eligibility. | Defect for precondition, reproduced. | P0 |
| M07 | Out-of-order observations do not overwrite stronger current evidence. | Open. | P1 |
| M08 | Conflicting current hypotheses are handled explicitly. | Partial; replay creates ambiguous duplicate current beliefs. | P1 |
| M09 | Snapshot stays coherent during writer activity. | Open; multi-query consistency risk. | P1 |
| M10 | Large histories preserve decisive evidence within context budget. | Open; no selection/size budget. | P1 |
| M11 | Changing a dependency removes an inapplicable procedure; unrelated changes do not. | Open; useful graph-necessity test. | P0 |
| M12 | Branches, cycles, duplicate edges, missing services and paths over four hops have documented outcomes. | Open; fixed topology only. | P2 |
| M13 | A tool can be reconsidered after relevant context changes without blind retries. | Defect for generalized use; blanket blacklist. | P2 |
| C01 | Eight independent claimants produce one owner. | Pass; not synchronized load benchmarking. | P0 |
| C02 | Old owner cannot append after handoff or lease replacement. | Pass. | P0 |
| C03 | Expired unstarted claim can be reclaimed. | Pass, forced expiry test. | P0 |
| C04 | Running uncertain action cannot be automatically reclaimed. | Pass. | P0 |
| C05 | Slow model completion after lease expiry cannot dispatch a tool. | Open, although database fencing exists. | P1 |
| C06 | Two same-token action starts cannot both execute. | Open direct race test. | P1 |
| C07 | Repeated claim/write races under load preserve invariants and report latency. | Open. | P2 |
| C08 | Clock skew and boundary-time expiry have documented semantics. | Open; host wall clocks. | P2 |
| T01 | Repeat completed sandbox operation returns same receipt. | Pass. | P0 |
| T02 | Same operation ID with different tool is rejected. | Source guard present; dedicated test open. | P1 |
| T03 | Receipt operation/tool/case mismatch cannot finish another action. | Defect at library boundary. | P1 |
| T04 | False, stale or pre-action health evidence cannot resolve. | Defect for false payload; remaining variants open. | P1 |
| T05 | Lost response leaves task safe and offers reconciliation. | Partial: safe blocking passes; recovery absent. | P0 |
| T06 | Kill at each reservation/effect/receipt/graph boundary avoids duplicate remediation. | Open; timeout test is narrower than these crash windows. | P1 |
| T07 | No action dispatched after a confirmed pre-action transport error; claim released. | Partial: no action, but claim retained. | P0 |
| T08 | A successful action followed by failed final probe is explainable and recoverable. | Open; limited handoff path exists. | P1 |
| T09 | Concurrent sandbox cases cannot invalidate one another's health. | Defect in isolation claim; shared subprocess. | P2 |
| A01 | Invented or cross-incident citation IDs are rejected. | Pass for invented IDs; graph evidence isolation also tested. | P0 |
| A02 | Irrelevant, duplicate and superseded citations are distinguished from valid support. | Defect for irrelevant/duplicate citations. | P1 |
| A03 | Malformed JSON, missing fields, extra fields and unknown tools dispatch nothing. | Partial: schema exists; full response matrix open. | P1 |
| A04 | Model error releases a pre-dispatch claim. | Pass with mocked model failure. | P0 |
| A05 | Missing model, HTTP timeout, 429, 5xx and blocked/empty Gemini result are recoverable. | Partial: missing configuration tested; error/UI matrix open. | P1 |
| A06 | Prompt injection in memory cannot bypass tools, scope or evidence gates. | Open; system instruction alone is not proof. | P1 |
| A07 | Model handoff and unsafe proposed restart are recorded honestly. | Partial: code paths; end-to-end adverse model cases open. | P1 |
| A08 | Paired memory/no-memory runs use identical current evidence and budgets. | Open; no evaluation artifact. | P0 |
| A09 | Changed-fact variant tests use of current versus superseded knowledge. | Open. | P1 |
| I01 | Same names in different tenant graphs do not mix evidence. | Pass for tested graph scopes. | P0 |
| I02 | Same-tenant cross-incident evidence cannot support a hypothesis. | Pass. | P0 |
| I03 | Authenticated tenant A cannot read/claim tenant B. | Absent; API deliberately local and unauthenticated. | P2 unless hosted |
| I04 | Read snapshots never expose claim tokens. | Pass for existing assertions; inspect all future endpoints. | P1 |
| I05 | Invalid tenant identifiers are rejected without query injection. | Pass for tested inputs; Cypher values parameterized. | P0 |
| G01 | Graphiti driver/index setup is isolated from operational graph. | Pass. | P1 |
| G02 | First new episode is ingested. | Defect, `NodeNotFoundError`, reproduced. | P1 if advertised |
| G03 | Repeated/partial/concurrent exports neither skip unfinished work nor duplicate it. | Open; completion/locking design incomplete. | P2 |
| G04 | Semantic retrieval respects tenant and fact validity with source provenance. | Open end-to-end; driver isolation is insufficient. | P2 |
| G05 | Quota/embedding-dimension/provider failure leaves operational memory usable. | Open; bridge is optional, core has no bridge dependency. | P2 |
| U01 | Graph visual changes when source relationships change. | Defect, hardcoded. | P0 |
| U02 | Latest decision and its citations match the executed attempt. | Defect, first decision selected. | P1 |
| U03 | Browser refresh after completion restores incident. | Partial: earlier walkthrough; no new browser verification here. | P0 |
| U04 | Transient restore outage preserves saved incident identity. | Defect in catch handler. | P0 |
| U05 | Lost mutation response reloads current state before retry. | Defect, no reload. | P0 |
| U06 | Connection, lease, running/uncertain status and freshness remain accurate over time. | Partial/defect; no continuous refresh. | P1 |
| U07 | Provider availability and API environment loading are clear. | Open; always-enabled selector. | P1 |
| U08 | Keyboard focus, readable evidence, 200% zoom, narrow viewport and long errors work. | Open; small text and select focus concern identified. | P1 |
| U09 | Request cancellation, offline/reconnect and two-tab interaction do not misrepresent server completion. | Open. | P1 |
| R01 | Clean checkout installs with locked dependencies and documented runtime versions. | Open; existing environment build passed. | P0 |
| R02 | Occupied ports, Docker unavailable and wrong backend URL produce actionable setup errors. | Open. | P1 |
| R03 | Required source/video links are publicly accessible in a signed-out browser. | Open/missing evidence. | P0 |
| R04 | Submission declares actual tracks, AI assistance and limitations. | Partial: README disclosure/Track 02 exist. | P0 |
| R05 | Participant can explain ownership guards, graph queries and uncertainty handling. | Unverified; must be demonstrated personally. | P0 |

## What to do next, in order

1. **Repair the visible contract and unsafe stage behavior.** Fix F02–F05 and the transient case-loss path. Add focused regression checks that fail on the reproduced inputs. Make current facts and current decisions accurate.
2. **Make the handoff proof inspectable.** Show actual separate workers or use the already working CLI boundary. Display retrieved failure evidence, selected context, relevant Cypher and a traceable action/result chain. Add receipt reconciliation or an explicit auditable manual recovery path for uncertainty.
3. **Measure the central claim.** Run a small paired evaluation on the existing case and a history-sensitive variant. Keep tools/current observations/budgets equal. Report raw outcomes, proposed versus executed repeated actions, stale-fact use, citation relevance, token use and latency. Three paired runs per scenario are a practical starting point, not a statistical confidence guarantee. Neutral results are acceptable; fabricated improvement is not.
4. **Finish the submission package.** Public repository, tested minimal setup, truthful architecture/model, relevant queries and a clear video. Reserve recording and verification time before adding optional functionality.
5. **Keep direct FalkorDB and local Mistral as the main path.** They work. Fix/timebox Graphiti only if a concrete demonstrated semantic feature needs it. Do not add Cognee, a second domain, public multi-user hosting or an MCP integration simply for the feature list.

The previously reviewed winners suggest clear stories, visible evidence and bounded failure handling—not merely attractive dashboards. Relay has adopted the story and visual structure, but its hardcoded graph, weak recovery UI and missing comparative evidence leave that strategy only partly implemented. See [the earlier winner research and its stated limits](../research/winner-strategies.md); this review did not re-audit those projects or infer an unpublished judging rubric from them.

## Questions a skeptical judge will ask

- Which exact historical fact changed the successor's action? Would it choose the same repair from `/inspect` alone?
- Show the first agent terminating and a new process retrieving state. What is copied through memory versus explicitly passed on the command line?
- Remove a relevant graph edge or procedure. Does eligibility and the on-screen explanation change?
- Why is FalkorDB appropriate beyond being required? Explain relationship traversal, evidence history and shared ownership. Do not claim that another database could never implement the same application.
- What happens if the repair executes but the response is lost? Which receipt and operation identity prevent a duplicate?
- Why is the fault still shown as current after recovery? Which timestamp means observation time and which means write time?
- Can an agent cite an irrelevant episode? Does “valid citation” mean existence, relevance or proof?
- What did the model actually decide? What was deliberately scripted, and which mode was used in the recording?
- Is Graphiti used by the successor, and has first ingestion actually succeeded?
- What does tenant isolation guarantee here, and what does it not guarantee?
- What original decisions and verification did the participant perform, and can they explain the conditional Cypher writes without the coding assistant?

The strongest submission claim currently supportable is: **Relay persists incident evidence and fenced ownership in FalkorDB; a separate CLI successor can retrieve that state, avoid prohibited repeated execution, make a bounded local-model repair choice, and verify recovery in a synthetic HTTP sandbox.** Stronger claims about measured intelligence gains, autonomous diagnosis, learned procedures, working Graphiti semantics, production isolation or high concurrency need additional evidence.
