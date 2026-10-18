import json

import httpx
import pytest

from relay.config import sandbox_case, tenant_graph
from relay.models import decide


def test_tenant_names_are_unambiguous_and_namespaces_separate():
    assert tenant_graph("acme") != tenant_graph("Acme")
    assert tenant_graph("acme", "memory") != tenant_graph("acme", "graphiti")
    assert sandbox_case("a", "bc") != sandbox_case("ab", "c")


@pytest.mark.parametrize("tenant", ["", "../acme", "acme' MATCH (n)", "a" * 65])
def test_invalid_tenants_rejected(tenant):
    with pytest.raises(ValueError):
        tenant_graph(tenant)


def test_model_cannot_cite_invented_evidence(monkeypatch):
    def response(_self, _url, **_kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", "http://localhost"),
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "tool": "restore_inventory_route",
                            "reason": "Fix it",
                            "evidence_ids": ["invented"],
                        }
                    )
                }
            },
        )

    monkeypatch.setattr(httpx.Client, "post", response)
    with pytest.raises(ValueError, match="outside this incident"):
        decide({"episodes": [{"id": "real"}]}, "ollama")


def test_model_prompt_contains_copyable_evidence_catalog(monkeypatch):
    seen = {}

    def response(_self, _url, **kwargs):
        seen["system"] = kwargs["json"]["messages"][0]["content"]
        return httpx.Response(
            200,
            request=httpx.Request("POST", "http://localhost"),
            json={
                "message": {
                    "content": json.dumps(
                        {"tool": "handoff", "reason": "Need evidence", "evidence_ids": ["ep1"]}
                    )
                }
            },
        )

    monkeypatch.setattr(httpx.Client, "post", response)
    decide(
        {
            "episodes": [{"id": "ep1", "kind": "observation", "content": "Down"}],
            "failed_actions": [{"tool": "restart_inventory"}],
            "procedures": [
                {"name": "restart_inventory"},
                {"name": "restore_inventory_route"},
            ],
        },
        "ollama",
    )
    assert '"id": "ep1"' in seen["system"]
    assert "ALLOWED EVIDENCE" in seen["system"]
    assert 'FORBIDDEN TOOL NAMES: ["restart_inventory"]' in seen["system"]
    assert 'ELIGIBLE ACTION TOOLS: ["restore_inventory_route"]' in seen["system"]
    assert "FAILED ACTION RECEIPT EPISODE IDs" in seen["system"]


def test_gemini_requires_explicit_configuration(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        decide({"episodes": []}, "gemini")
