# Strategies adapted from previous winners

The published Scrape-Verse winners consistently made one useful workflow easy to understand, showed evidence inside the interface, and backed the demo with reproducible engineering artifacts.

## Applied to Relay

| Winning pattern | Relay implementation |
| --- | --- |
| Tell one clear story | Checkout incident → failed restart → handoff → graph recall → safe recovery |
| Make state visible | The console shows owner, handoff generation, worker IDs, memory events, hypotheses, and receipts |
| Show the core technology | FalkorDB paths, evidence links, procedures, claims, and Cypher-backed guards appear in the demo |
| Bound autonomous behavior | The model selects one allowlisted action and cites exact evidence IDs |
| Verify outcomes | Resolution requires a separate HTTP health probe after the action receipt |
| Provide reproducible evidence | Lockfiles, public CI, integration tests, and raw evaluation outputs ship with the repository |
| Handle interruptions | Operation IDs and stored receipts support reconciliation without replaying the tool |

## Demo sequence

1. Initialize the synthetic checkout incident.
2. Run Agent A and show its distinct process identity and failed restart receipt.
3. Exercise the FalkorDB guard against repeating that action.
4. Launch the successor with local Mistral or Gemini.
5. Show retrieved memory, exact citations, the dependency path, and the applicable procedure.
6. Show the corrective receipt and independent checkout recovery probe.
7. End on the public repository, passing workflow, and raw paired evaluation artifact.

## Presentation priorities

- Keep the Track 02 memory-and-coordination story central.
- Use the graph to explain why the successor chose its action.
- Keep the model, retrieval, guard, action, and verification stages visually distinct.
- Show real process IDs and run IDs so the handoff is concrete.
- Use the recorded deterministic-policy run as a reliable backup and label it clearly.

## Sources

- [Scrape-Verse projects](https://www.wemakedevs.org/hackathons/scrape-verse/projects)
- [ScrapeSentry](https://github.com/himanshu748/scrapesentry)
- [PriceGuardAI recovery implementation](https://github.com/Kartikey-Kesarwani-2005/PriceGuardAI/blob/main/lib/healer.js)
