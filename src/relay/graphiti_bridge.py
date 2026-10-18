"""Optional semantic memory on FalkorDB, separate from operational coordination.

No model clients are constructed by the core demo. Sync is an explicit command
and requires Gemini configuration. The no-inference probe tests only the driver.
"""

import os
from datetime import datetime, timezone

from relay.config import Settings, tenant_graph
from relay.memory import Memory


async def probe(tenant: str) -> dict:
    from graphiti_core.driver.falkordb_driver import FalkorDriver

    settings = Settings.from_env()
    graph_name = tenant_graph(tenant, "graphiti")
    driver = FalkorDriver(host=settings.host, port=settings.port, database=graph_name)
    try:
        await driver.build_indices_and_constraints()
        await driver.execute_query(
            "MERGE (p:RelayProbe {name:$name}) RETURN p.name AS name", name=tenant
        )
        records, _, _ = await driver.execute_query(
            "MATCH (p:RelayProbe {name:$name}) RETURN p.name AS name", name=tenant
        )
        if not records or records[0]["name"] != tenant:
            raise RuntimeError("Graphiti driver probe failed")
        return {"graph": graph_name, "driver": "passed", "inference_tested": False}
    finally:
        await driver.close()


def client_for(tenant: str):
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("RELAY_GEMINI_MODEL")
    if not key or not model:
        raise ValueError("Graphiti sync requires GEMINI_API_KEY and RELAY_GEMINI_MODEL")
    os.environ.setdefault("GRAPHITI_TELEMETRY_ENABLED", "false")
    from graphiti_core import Graphiti
    from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
    from graphiti_core.driver.falkordb_driver import FalkorDriver
    from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
    from graphiti_core.llm_client.config import LLMConfig
    from graphiti_core.llm_client.gemini_client import GeminiClient

    settings = Settings.from_env()
    config = LLMConfig(api_key=key, model=model, small_model=model, temperature=0)
    return Graphiti(
        graph_driver=FalkorDriver(
            host=settings.host, port=settings.port, database=tenant_graph(tenant, "graphiti")
        ),
        llm_client=GeminiClient(config=config),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=key,
                embedding_model=os.getenv("RELAY_GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
                embedding_dim=768,
            )
        ),
        cross_encoder=GeminiRerankerClient(config=config),
        max_coroutines=1,
    )


async def sync(tenant: str, incident: str) -> dict:
    from graphiti_core.nodes import EpisodeType

    memory = Memory(tenant)
    context = memory.snapshot(incident)
    graphiti = client_for(tenant)
    graph_name = tenant_graph(tenant, "graphiti")
    imported = []
    try:
        await graphiti.build_indices_and_constraints()
        # Explicit, serial export. Source UUIDs allow retries to skip completed episodes.
        # Do not run two exporters for the same tenant concurrently in this prototype.
        for episode in context["episodes"]:
            records, _, _ = await graphiti.driver.execute_query(
                "MATCH (e:Episodic {uuid:$uuid}) RETURN e.uuid AS uuid", uuid=episode["id"]
            )
            if records:
                continue
            body = (
                f"Incident {incident}. Agent {episode['agent']}. "
                f"{episode['kind']}: {episode['content']}. "
                f"Evidence payload: {episode.get('payload', '{}')}"
            )
            await graphiti.add_episode(
                name=f"{incident}:{episode['kind']}",
                episode_body=body,
                source=EpisodeType.text,
                source_description=f"Relay synthetic episode {episode['id']}",
                reference_time=datetime.fromtimestamp(episode["created_at"], timezone.utc),
                group_id=graph_name,
                uuid=episode["id"],
            )
            imported.append(episode["id"])
        return {"graph": graph_name, "imported_episode_ids": imported}
    finally:
        await graphiti.close()


async def search(tenant: str, query: str) -> list[dict]:
    graphiti = client_for(tenant)
    try:
        results = await graphiti.search(
            query, group_ids=[tenant_graph(tenant, "graphiti")], num_results=5
        )
        return [
            {
                "id": edge.uuid,
                "fact": edge.fact,
                "episodes": edge.episodes,
                "valid_at": str(edge.valid_at),
                "invalid_at": str(edge.invalid_at),
            }
            for edge in results
        ]
    finally:
        await graphiti.close()
