# Copyright 2024 Topoteretes UG
# SPDX-License-Identifier: Apache-2.0
# Modified for Relay: dictionary inputs; lexical/graph lanes instead of vector/summary;
# retain scores; remove truth/personal weighting and Cognee runtime dependencies.
# Derived from cognee/modules/retrieval/hybrid/ranking.py and
# cognee/modules/retrieval/utils/brute_force_triplet_search.py (format_triplets).
# Upstream revision: 37f788bd287750e10d7610173e5332b3843f6ebd
# See LICENSE, NOTICE.md and PROVENANCE.json in this directory.


def rank_candidates(pairs: list[dict], limit: int) -> list[dict]:
    """Cognee's reciprocal-rank fusion with bounded importance weighting.

    Ranks are zero-based. The inputs here are lexical and graph-evidence ranks;
    this is deliberately not represented as vector/embedding search.
    """
    if limit <= 0:
        return []
    rrf_k = max(30, min(60, 20 + 2 * limit))
    ranked = []
    for pair in pairs:
        ranks = [r for r in (pair.get("lexical_rank"), pair.get("graph_rank")) if r is not None]
        if not ranks:
            continue
        rrf_score = sum(1.0 / (rrf_k + rank + 1) for rank in ranks)
        raw = pair.get("importance_weight", 0.5)
        importance = raw if isinstance(raw, (int, float)) else 0.5
        importance = max(0.0, min(1.0, importance))
        final_score = rrf_score * (0.75 + 0.5 * importance)
        item = {**pair, "score": final_score, "rrf_score": rrf_score}
        ranked.append((final_score, rrf_score, min(ranks), pair["id"], item))
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
    return [pair for *_, pair in ranked[:limit]]


def format_triplets(edges: list[dict]) -> str:
    """Adapted Cognee triplet formatter; dictionaries replace Cognee Edge objects."""
    triplets = []
    for edge in edges:
        node1_info = {k: v for k, v in edge["source"].items() if v is not None}
        node2_info = {k: v for k, v in edge["target"].items() if v is not None}
        edge_info = {k: v for k, v in edge["attributes"].items() if v is not None}
        triplets.append(f"Node1: {node1_info}\nEdge: {edge_info}\nNode2: {node2_info}\n\n\n")
    return "".join(triplets)
