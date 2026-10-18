import os
from uuid import uuid4

import pytest

from relay.memory import Memory


def pytest_collection_modifyitems(items):
    if os.getenv("RELAY_INTEGRATION") != "1":
        skip = pytest.mark.skip(reason="Set RELAY_INTEGRATION=1 with docker compose running")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def memory():
    store = Memory("test-" + uuid4().hex)
    try:
        yield store
    finally:
        # Only this fixture's unique graph; never delete demo or user graphs.
        if store.graph_name in store.db.list_graphs():
            store.graph.delete()
