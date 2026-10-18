import asyncio
from uuid import uuid4

import pytest

from relay.config import tenant_graph
from relay.graphiti_bridge import client_for, probe
from relay.memory import Memory


def test_graphiti_never_defaults_to_an_unconfigured_provider(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="requires GEMINI_API_KEY"):
        client_for("test")


@pytest.mark.integration
def test_graphiti_driver_and_indexes_are_isolated_from_operational_memory():
    pytest.importorskip("graphiti_core")
    tenants = ["test-" + uuid4().hex for _ in range(2)]
    stores = [Memory(tenant) for tenant in tenants]
    try:
        for tenant, store in zip(tenants, stores, strict=True):
            result = asyncio.run(probe(tenant))
            assert result["driver"] == "passed"
            assert result["inference_tested"] is False
            assert result["graph"] != store.graph_name
        for tenant, store in zip(tenants, stores, strict=True):
            graph = store.db.select_graph(tenant_graph(tenant, "graphiti"))
            assert graph.query("MATCH (p:RelayProbe) RETURN p.name").result_set == [[tenant]]
    finally:
        for tenant, store in zip(tenants, stores, strict=True):
            name = tenant_graph(tenant, "graphiti")
            if name in store.db.list_graphs():
                store.db.select_graph(name).delete()
