"""Incident-scoped FalkorDB retrieval using attributed Cognee-derived primitives.

No inference, embeddings, external database or provider credentials are required.
Relay supplies scope, safety pins, temporal policy and evidence provenance.
"""

import hashlib
import json
import re

from relay._vendor.cognee.retrieval import format_triplets, rank_candidates
from relay.memory import Memory

CANDIDATES = """
MATCH (i:Incident {id:$incident})-[:HAS_EPISODE]->(e:Episode)
WHERE e.kind IN ['observation','configuration','action_result','handoff','guard_rejection']
OPTIONAL MATCH (e)-[:SUPPORTS]->(h:Hypothesis)
WHERE h.current=true
WITH e, count(h) AS current_support
ORDER BY e.created_at DESC, e.id LIMIT 256
RETURN properties(e), current_support
"""


def retrieve(memory: Memory, incident: str, query: str, limit: int = 8) -> dict:
    if not query.strip() or len(query) > 500 or not 2 <= limit <= 20:
        raise ValueError("Recall requires a 1–500 character query and a limit from 2 to 20")
    info = memory.incident(incident)
    rows = memory.rows(CANDIDATES, incident=incident)
    episodes = {r[0]["id"]: r[0] for r in rows}
    terms = set(re.findall(r"[a-z0-9_]+", query.lower()))
    support = {r[0]["id"]: r[1] for r in rows}
    relevance = {}
    for event in episodes.values():
        words = set(
            re.findall(r"[a-z0-9_]+", (event["content"] + " " + event.get("payload", "")).lower())
        )
        relevance[event["id"]] = len(terms & words)
    lexical = sorted(episodes, key=lambda key: (-relevance[key], -episodes[key]["created_at"], key))
    structural = sorted(
        episodes,
        key=lambda key: (
            -support[key],
            -int(episodes[key]["kind"] in {"configuration", "action_result"}),
            -episodes[key]["created_at"],
            key,
        ),
    )
    pairs = [
        {
            "id": key,
            "lexical_rank": lexical.index(key) if relevance[key] else None,
            "graph_rank": structural.index(key),
            "importance_weight": 1.0 if support[key] else 0.5,
        }
        for key in episodes
    ]
    ranked = rank_candidates(pairs, limit)
    # Safety-critical facts must survive relevance ranking. They are still scoped by graph.
    latest_config = next((e["id"] for e in episodes.values() if e["kind"] == "configuration"), None)
    failures = memory.rows(
        "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(:Task)-[:HAS_ATTEMPT]->"
        "(a:Action {status:'failed'})-[:HAS_RESULT]->(e:Episode) "
        "RETURN properties(a), properties(e) ORDER BY a.started_at DESC LIMIT 20",
        incident=incident,
    )
    pinned = ([latest_config] if latest_config else []) + [r[1]["id"] for r in failures]
    for _, event in failures:
        episodes[event["id"]] = event
    selected = list(dict.fromkeys(pinned + [r["id"] for r in ranked]))[: max(limit, len(pinned))]
    paths = [
        r[0]
        for r in memory.rows(
            "MATCH (:Incident {id:$incident})-[:AFFECTS]->(s:Service), "
            "p=(s)-[:DEPENDS_ON*1..4]->(:Service) "
            "RETURN [n IN nodes(p)|n.name], length(p) AS hops ORDER BY hops LIMIT 40",
            incident=incident,
        )
    ]
    procedures = [
        r[0]
        for r in memory.rows(
            "MATCH (:Incident {id:$incident})-[:AFFECTS]->(:Service)"
            "-[:DEPENDS_ON*1..4]->(s:Service)<-[:APPLIES_TO]-(p:Procedure) "
            "RETURN DISTINCT properties(p) LIMIT 20",
            incident=incident,
        )
    ]
    beliefs = [
        r[0]
        for r in memory.rows(
            "MATCH (:Incident {id:$incident})-[:HAS_HYPOTHESIS]->(h:Hypothesis) "
            "WHERE h.current=true RETURN properties(h) LIMIT 20",
            incident=incident,
        )
    ]
    triples = []
    seen = set()
    for path in paths:
        for a, b in zip(path, path[1:]):
            if (a, b) not in seen:
                seen.add((a, b))
                triples.append(
                    {
                        "source": {"name": a},
                        "attributes": {"relation": "DEPENDS_ON"},
                        "target": {"name": b},
                    }
                )
    for p in procedures:
        triples.append(
            {"source": p, "attributes": {"relation": "APPLIES_TO"}, "target": {"name": p["target"]}}
        )
    context = {
        "incident": info,
        "episodes": [episodes[key] for key in selected],
        "hypotheses": beliefs,
        "procedures": procedures,
        "failed_actions": [{k: v for k, v in r[0].items() if k != "token"} for r in failures],
        "graph_context": format_triplets(triples),
    }
    # Fail closed if mandatory evidence cannot fit; do not silently truncate a safety fact.
    while len(json.dumps(context).encode()) > 18000:
        removable = next((e for e in reversed(context["episodes"]) if e["id"] not in pinned), None)
        if removable is None:
            raise ValueError("Required evidence exceeds context budget; narrow the incident")
        context["episodes"].remove(removable)
    encoded = json.dumps(context, sort_keys=True).encode()
    scores = {r["id"]: r for r in ranked}
    manifest = {
        "engine": "Relay recall · Cognee-derived RRF + triplet context",
        "upstream_revision": "37f788bd287750e10d7610173e5332b3843f6ebd",
        "query": query,
        "candidate_count": len(episodes),
        "candidate_window": 256,
        "context_bytes": len(encoded),
        "context_sha256": hashlib.sha256(encoded).hexdigest(),
        "selected": [
            {
                "id": e["id"],
                "kind": e["kind"],
                "content": e["content"],
                "score": scores.get(e["id"], {}).get("score"),
                "reason": "required current configuration / failed action"
                if e["id"] in pinned
                else "lexical and graph-evidence reciprocal-rank fusion",
            }
            for e in context["episodes"]
        ],
        "triplets": triples,
    }
    return {"context": context, "manifest": manifest}
