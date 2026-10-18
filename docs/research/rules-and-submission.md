# Rules and submission

Verified October 5, 2026 against the [official rules](https://www.wemakedevs.org/hackathons/falkordb/rules). Recheck before building and submitting; this note is not a replacement for the rules.

## Requirements

- Solo entry is allowed; teams have at most four people.
- Build window: **October 15, 2026, 12:01 AM IST–October 18, 2026, 11:59 PM IST**.
- Main coding and design start within that window. Earlier idea discussions, notes, graph sketches, and diagrams are permitted.
- FalkorDB must power central functionality as the primary graph database. A decorative graph is insufficient.
- Docker, self-hosting, and Cloud are accepted; frameworks and public libraries are permitted.
- Multiple tracks are allowed; identify each entered track.
- Use permitted public, synthetic, or own data; exclude private, personal, login-protected, paywalled, or restricted information.
- Disclose AI assistance and understand the submitted code and technical decisions.
- Track 02's listed prize is a PS5 with GTA VI; Track 01's is an iPhone 18 Pro.

## Submission checklist

- [x] Public source repository.
- [x] README with setup and graph model.
- [x] Essential Cypher queries or graph algorithms.
- [ ] Working demo video.
- [x] Live deployment or complete local setup.
- [x] Entered tracks identified.

## Current build status — October 18

The research-only boundary ended when the event opened. Relay now has a working local FalkorDB application, synthetic incident sandbox, React console, separate worker processes, Cognee-derived retrieval, model/policy modes, automated verification, and a [public source repository](https://github.com/PratikPawar1401/relay-agent-memory) with passing GitHub Actions. The demo video remains a submission blocker; a public deployment is optional because the complete local setup is documented. Current release status lives in [`TODOS_ASAP.md`](../../TODOS_ASAP.md) and [`docs/submission.md`](../submission.md); the dated research above remains as the original rules record.
