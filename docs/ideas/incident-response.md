# Incident-response demo

Relay helps a replacement incident agent continue from durable operational memory instead of reconstructing the previous worker's investigation.

## Restart-and-handoff scenario

1. The sandbox creates a checkout outage caused by an invalid inventory route.
2. Agent A records the outage, forms an initial hypothesis, and attempts a restart.
3. The restart receipt shows that service health did not recover.
4. Agent A hands off and exits.
5. A guard demonstrates that the failed restart cannot be repeated.
6. A fresh successor retrieves the prior evidence, dependency path, current configuration, and recovery procedure.
7. Local Mistral or Gemini chooses a bounded action and cites stored episode IDs.
8. Relay executes the eligible repair and resolves the incident after an independent HTTP probe.

## User value

- Durable context survives process boundaries.
- Shared ownership prevents competing workers from acting simultaneously.
- Historical and current beliefs remain explainable.
- Decisions point to exact evidence.
- Receipts and health probes establish what happened after a tool call.

## Measurements

- Valid cited decisions with and without incident history.
- Repeated failed actions executed after handoff.
- Claim winners under contention.
- Recovery receipts correlated to their reserved operation IDs.
- Context size, selected episode IDs, provider usage, and worker identity.
