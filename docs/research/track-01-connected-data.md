# Track 01: Agents That Act on Connected Data

Research date: October 5, 2026. Secondary opportunity using the same product.

## Official focus

The event highlights multi-hop reasoning, graph queries or algorithms exposed as tools, MCP-based tool selection, actions informed by relationships, and explainable outcomes. [Event tracks](https://www.wemakedevs.org/hackathons/falkordb)

## Proposed application

Investigate a symptom through a service dependency chain: checkout fails because inventory cannot reach its backing service after a configuration change. The agent should retrieve the relevant path, correlate the change with observations, and select a bounded sandbox action.

| Investigation | Graph contribution | Possible demonstration |
| --- | --- | --- |
| What could cause this symptom? | Traverse dependencies from the affected service | Display the path actually returned by the query |
| What changed nearby? | Connect observations and changes to affected dependencies | Identify a candidate cause with source evidence |
| Which fix is appropriate? | Relate candidate procedures to preconditions and previous outcomes | Avoid an earlier ineffective restart |
| Did the action work? | Connect the action to subsequent health observations | Show an independently measured recovery |

## Research boundaries

- Explore a small allowlisted tool set: inspect health, read synthetic logs, restart a sandbox service, and restore a known configuration.
- Investigate MCP only if it adds demonstrable tool-selection value without compromising the primary memory demo.
- Do not add PageRank or other algorithms solely to increase the feature count. Dependency traversal may be sufficient for the scenario.
- Graph evidence should affect the chosen action; the UI should expose the query result used, not reconstruct an explanation afterward.
- Keep operations inside the local sandbox. Production infrastructure access is outside this concept.

These are proposed product constraints, not extra competition requirements.

## Proposed evaluation

Check that changing a relevant dependency or invalidating evidence changes the decision appropriately. Use unrelated graph changes as controls. Verify recovery through a health check independent of the agent's verbal conclusion.

Demonstrate what fails when graph context is unavailable: diagnosis or action eligibility should become unsupported, and the system should report that limitation. Do not silently substitute hard-coded incident answers.

Only enter this secondary track if the working build demonstrates graph-driven action convincingly. Track 02 remains the priority. See [Track 02 research](track-02-memory-and-coordination.md).
