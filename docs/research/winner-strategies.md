# What Relay can learn from Scrape-Verse winners

Research date: October 17, 2026. This is a strategy review, not an implementation report or a claim about unpublished judging decisions.

## Evidence and review limits

Award names were verified against the [organizer's winners page](https://www.wemakedevs.org/hackathons/scrape-verse/projects). Reviewed linked repositories, project documentation, a recovery implementation, and ScrapeSentry's demo script/design notes. Repositories may have changed since judging; their current contents do not establish what was demonstrated at submission time.

PriceGuardAI's live deployment was visually reviewed in Chrome on October 17, 2026. ScrapeSentry's deployment opened but rendered a blank page after reload, so its live interface was not assessed. No submission videos were reviewed. Do not interpret the findings below as a complete code audit or independent reproduction of their results.

## Verified project-award winners

| Project | Award | Reviewed artifact and transferable lesson |
| --- | --- | --- |
| Research Factory | Grand prize | Its current [specification](https://github.com/bgoconnor/port-brightdata-signoz-hackathon-kit/blob/main/SPEC.md) distinguishes running code from evidence supporting a claim, and defines a feature cut order. Define Relay's proof before adding scope. |
| ScrapeSentry | Best UI | Its [README](https://github.com/himanshu748/scrapesentry) describes a brief guided recovery workflow and clearly labeled recorded provider evidence. Give judges an easy path through the story. |
| PriceGuardAI | Best Clean Code | Its [recovery implementation](https://github.com/Kartikey-Kesarwani-2005/PriceGuardAI/blob/main/lib/healer.js) bounds retries, applies a healing cooldown, reruns after healing, and explicitly marks cached fallback. Make failure states visible and bounded. |
| Trainable | Best Use of Bright Data | Its [README](https://github.com/meowshmalloww/Trainable) separates deterministic validation from learned-policy runs and describes evidence-backed assets. Explain exactly which Relay steps are model-driven. |
| The Scraper Factory | Best Use of Port | Its [README](https://github.com/Nitishmane/scraper-factory) separates agent judgment from deterministic verification and makes Port's stored context part of the product path. Make FalkorDB's operational role demonstrable. |
| InflationForge | Best Use of SigNoz | Its [README](https://github.com/KaushikSiva/Inflation-Forge) connects observations to source receipts and trace IDs. Connect every visible Relay outcome to its underlying evidence. |

These six are project awards. The event also lists a social-post award and a raffle; those are not evidence of technical project quality. The Top 50 list is distinct from the award winners.

## Live interface observations

PriceGuardAI's deployed interface adds several presentation lessons that were not clear from repository reading alone:

- The landing screen states one concrete promise, then immediately shows the main action, operational scope, and key signals. Relay should open directly on the active incident and recovery objective.
- Synthetic content is visibly marked **Demo feed** beside affected store and product data. Relay should label scenario fixtures, saved replays, and live model output at the point where they appear.
- The interface exposes data freshness as a product concept: live, recently updated, and stale. Relay should show the age and status of retrieved episodes and current observations instead of treating every memory as equally current.
- Store health and self-healing sit inside the same user workflow, while detailed scraper monitors are placed under an **Advanced** disclosure. Relay should keep ownership, handoff, evidence, and outcome in the primary view, with raw Cypher and diagnostic metadata available on demand.
- Recommendations include short evidence phrases such as current value, historical average, trend, and source. Relay's action card should pair the chosen remediation with cited episode IDs, the relevant observation, and the expected outcome.
- The deployment distinguishes demo data from operational results, but its store reliability counters showed zero checks and zero self-heals during review. A polished surface does not replace a live proof; Relay's headline metrics must come from the demonstrated incident run or be clearly labeled fixtures.

These are direct observations of the current deployment, not claims about which version judges saw or why the project won Best Clean Code.

## Interpretation for Relay

The following priorities are our inference from the reviewed artifacts, not a transferable official scoring rubric. Scrape-Verse's categories differ from Graph Hacks Track 02.

### 1. Build the shortest demonstrable memory loop

Recommended pitch: **Relay lets a replacement incident agent continue with the evidence and failed attempts its predecessor left behind.**

Use the existing flow: service failure → unsuccessful restart → first process exits → successor reads FalkorDB → evidence changes the diagnosis → corrective action → independent health verification.

The backend already performs this flow. The missing piece is an interface that makes ownership, memory retrieval, and the consequence of that retrieval easy to see. Favor one incident console over multiple dashboards or a generic chatbot.

### 2. Show a rejected action as well as a successful one

Demonstrate an attempt to repeat the recorded failed restart. Show the guard rejecting it with the earlier action ID and outcome. Then show the successful route correction and its HTTP receipt.

The existing repeat-action guard and health probe provide the foundation. The interface should explain both. A rejection triggered deliberately by a demo control must be labeled as a guard test, not attributed to an actual model decision.

### 3. Separate memory infrastructure from model intelligence

Currently the first shift is scripted. Configuration inspection and hypothesis correction are also application logic. Mistral chooses a corrective action within that bounded workflow. Keep those distinctions visible in the demo and submission.

Do not claim autonomous diagnosis, learned procedural memory, or Graphiti contradiction handling from this implementation. Those require additional work and evidence. A working, honestly bounded model agent is stronger than overstating unverified capabilities.

### 4. Make the graph necessary and inspectable

Show the actual dependency path, retrieved failed action, evidence episode, and hypothesis history used during the run. Include the relevant parameterized query in an expandable evidence panel.

An unavailable FalkorDB instance should produce an explicit error, as it already does. A graph visualization alone does not demonstrate graph-dependent behavior. Our main evidence should be persisted state and queries affecting eligibility and context.

### 5. Make the public demonstration reliable without disguising replay

ScrapeSentry's [demo script](https://github.com/himanshu748/scrapesentry/blob/main/docs/demo-script.md) provides a timed shot list, measured claims, and explicit narration for recorded provider evidence. Relay can use the same discipline with its own implementation and presentation.

Offer distinct labels for live local-model execution, deterministic policy execution, and any saved run replay. A recording can accompany setup instructions, but it must not impersonate a live backend. Preserve one real successful model run with sanitized inputs, outputs, citations, timings, and health receipts.

### 6. Use visual design to explain state

ScrapeSentry's [design notes](https://github.com/himanshu748/scrapesentry/blob/main/brand.md) reserve colors for specific operational states and distinguish evidence typography from narrative typography. Borrow that principle, not its branding or exact styling.

Suggested Relay console:

- Top: incident health, current owner, execution mode, and connection state.
- Left: chronological observations, actions, process exit, and handoff events.
- Center: current decision with cited memory and a small relevant graph path.
- Right: current versus superseded hypotheses, plus the selected action's receipt.
- Controls: create scenario, run controlled first shift, start fresh successor, inspect evidence.

Use text and icons alongside color. Keep unknown, failed, running, and independently verified states distinct. Display model waiting time explicitly; the observed local call took about 23 seconds.

## Critical evaluation gap: persistence is not yet measured decision improvement

Our existing 21 passing tests establish important correctness properties, but they do not measure the model's benefit from memory. A successor can infer the route fix from fresh configuration evidence even without prior history. We must not present that easy scenario as proof of an improvement we have not measured.

Recommended evaluation:

1. Keep the model, current observations, tools, inference settings, and action budget identical.
2. Compare the same successor with and without retrieved historical memory. Optionally add transcript retrieval as a third condition if time permits.
3. Count the model's proposed repeated actions separately from executed repetitions. A code guard preventing execution is not proof the model remembered.
4. Report valid citations, current-versus-superseded fact usage, action counts, latency, and recovery success for every run.
5. Include a small case where earlier outcomes genuinely disambiguate the next action; do not remove current observations from only one condition or force the baseline to fail.
6. If both conditions choose the right action, report that result. Describe the persistence/coordination benefits separately.

For a small local-model study, three paired runs per scenario are a reasonable initial budget, not a statistical guarantee. Preserve unsuccessful runs and configuration details. Never invent percentages or multiply a single success into a broad reliability claim.

## Proposed three-minute recording

This is our suggested duration, not a verified Graph Hacks video limit.

| Time | On-screen proof |
| --- | --- |
| 0:00–0:20 | Name the user problem; show checkout unavailable and the active agent. |
| 0:20–0:50 | Run the controlled restart attempt; show the unsuccessful HTTP receipt saved in FalkorDB. |
| 0:50–1:15 | First process exits; start a distinct successor process and show retrieved history. |
| 1:15–1:45 | Show new evidence, the superseded hypothesis, and the model's cited action choice. |
| 1:45–2:10 | Execute the fix; independent HTTP probe verifies recovery. |
| 2:10–2:35 | Show a clearly labeled repeated-action rejection and the graph path/query behind the evidence. |
| 2:35–3:00 | State measured results and limitations; point to code, setup, and comparison evidence if completed. |

Do not cut through the handoff in a way that conceals whether a new process actually started. If model wait time is edited, label the cut or use an explicitly recorded run. Use only measured results in narration.

## Priority changes for the remaining build window

The [current Graph Hacks rules](https://www.wemakedevs.org/hackathons/falkordb/rules) specify October 18, 2026, 11:59 PM IST as the submission deadline. They permit complete local setup instructions instead of deployment. Do not assume another hackathon's video length, approval flow, or submission-editing policy applies here.

1. **P0: Judge-facing incident console.** Wire the existing backend into the visible workflow above. Avoid unrelated views.
2. **P0: Evidence and submission package.** Rehearse the video, retain a sanitized model-run artifact, document essential Cypher, and ensure the required public source repository and setup are accessible.
3. **P1: Honest memory comparison.** Measure decision quality separately from guard enforcement. Report even neutral or negative results.
4. **P1: Compact coordination proof.** Expose the tested eight-contender/single-owner result and tenant-isolation check as reproducible evidence, not throughput claims.
5. **P2: Graphiti/Gemini enrichment.** Timebox it; only promote it into the headline demo if extraction and retrieval are verified. Its presence is not a substitute for a clear Track 02 result.

Defer additional frameworks, new domains, generalized autonomous operations, and an observability-stack migration. Preserve time for recording and a clean-checkout setup check. This research adds no application features and does not change existing runtime behavior.
