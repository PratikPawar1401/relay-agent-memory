# Source register

Access dates use Asia/Kolkata. All entries below were reviewed on **October 5, 2026**. Live documentation and repository branches can change; these links are not pinned release guarantees.

## Primary sources

| Source | Supported claims | Limits |
| --- | --- | --- |
| [Official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) | Eligibility, timing, technology, data, submission, and disclosure requirements | Recheck before the event; summarized in the rules note |
| [Event overview and tracks](https://www.wemakedevs.org/hackathons/falkordb) | Published track focus areas and event positioning | No numerical judging weights found in the reviewed page |
| [Event resources](https://www.wemakedevs.org/hackathons/falkordb/resources) | Organizer-provided learning and community links | No confirmed LLM credit offer found; absence here does not rule out later offers |
| [Graphiti](https://github.com/getzep/graphiti) | Temporal facts, episodes, provenance, hybrid retrieval, FalkorDB integration | Documented, not locally tested; use a pinned release during implementation |
| [Cognee FalkorDB adapter](https://github.com/topoteretes/cognee-community/blob/main/packages/hybrid/falkordb/README.md) | Community adapter and graph/vector integration example | Example configuration may drift from installed releases |
| [Cognee compatibility report #142](https://github.com/topoteretes/cognee-community/issues/142) | A reported Cognee 1.3.0 / adapter 0.3.1 incompatibility | Version-specific reporter evidence, not our reproduction or a universal limitation |
| [FalkorDB Python client](https://github.com/FalkorDB/falkordb-py) | Direct Python integration option | Does not itself define agent memory or coordination policy |
| [FalkorDB documentation](https://docs.falkordb.com/) | Property graph, Cypher, local setup, and indexing capabilities | No project-specific performance or persistence result established |

## Evidence conventions

- **Official requirement:** stated by the organizer; cite the event source.
- **Documented capability:** described by the relevant project's documentation; not a test result.
- **Reported issue:** attributed to its reporter and version combination.
- **Proposal:** our product or evaluation idea; not a claimed organizer requirement.
- **Tested result:** reserved for a recorded command/scenario, versions, environment, and observed outcome. None yet.

## Open research questions

| Question | Next evidence needed | Decision affected |
| --- | --- | --- |
| Are sponsor model credits available? | Organizer announcement or explicit response | Model/provider budget |
| Is there a weighted judging rubric or video limit? | Published event/submission instructions | Demo priorities and packaging |
| What hardware is available for local models? | Local capability inspection and participant preference | Zero-spend feasibility |
| Which versions work together? | Event-time minimal integration run with recorded versions | Dependency pins |
| How are Graphiti groups mapped on FalkorDB? | Selected driver code plus two-scope retrieval tests | Isolation and graph layout |
| How should tasks be claimed safely? | Backend semantics and contested-claim tests | Coordination implementation |
| What is the ingestion cost and latency? | Measured calls/tokens/timing on synthetic episodes | Dataset size and model budget |
| Is the concept sufficiently differentiated? | Review public examples and identify reused versus original behavior | Scope and demo narrative |

Community questions are research tasks only. No organizer or other person has been contacted by this workspace setup.

## October 17 update: winner research

See [the winner strategy review](winner-strategies.md) for linked primary sources: the organizer's Scrape-Verse award list, the six project repositories, Research Factory's specification, ScrapeSentry's demo/design notes, and PriceGuardAI's recovery implementation. Award status is organizer-confirmed; project behaviors are source/documentation findings, not independent reproductions. Strategy recommendations are our inference. Live visual inspection was unavailable, and repository contents may postdate judging.
