import json

import httpx
import pytest

from relay.config import sandbox_case, tenant_graph
from relay.models import ProviderError, _gemini_decision, decide, gemini_status


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
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
        decide({"episodes": []}, "gemini")


def test_gemini_structured_decision_is_validated():
    decision = _gemini_decision(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "tool": "handoff",
                                        "reason": "Need another observation",
                                        "evidence_ids": ["ep1"],
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )
    assert decision.tool == "handoff"


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"promptFeedback": {"blockReason": "SAFETY"}}, "blocked"),
        ({"candidates": []}, "no decision"),
        ({"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": []}}]}, "empty"),
    ],
)
def test_gemini_empty_and_blocked_responses_are_typed(payload, message):
    with pytest.raises(ProviderError, match=message):
        _gemini_decision(payload)


def test_gemini_readiness_probe(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("RELAY_GEMINI_MODEL", "gemini-test")

    def response(_url, **_kwargs):
        return httpx.Response(200, request=httpx.Request("GET", "https://example.test"), json={})

    monkeypatch.setattr(httpx, "get", response)
    assert gemini_status() == {
        "configured": True,
        "available": True,
        "model": "gemini-test",
    }


def test_gemini_decide_sends_schema_and_returns_usage(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("RELAY_GEMINI_MODEL", "gemini-test")
    seen = {}

    def response(_self, url, **kwargs):
        seen["url"] = url
        seen["request"] = kwargs["json"]
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        {
                                            "tool": "handoff",
                                            "reason": "Preserve the case",
                                            "evidence_ids": ["ep1"],
                                        }
                                    )
                                }
                            ]
                        }
                    }
                ],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
            },
        )

    monkeypatch.setattr(httpx.Client, "post", response)
    decision, metadata = decide(
        {
            "episodes": [{"id": "ep1", "kind": "observation", "content": "Down"}],
            "failed_actions": [],
            "procedures": [],
        },
        "gemini",
    )
    assert decision.tool == "handoff"
    assert metadata["provider"] == "gemini"
    assert metadata["usage"]["promptTokenCount"] == 10
    assert seen["url"].endswith("/gemini-test:generateContent")
    assert seen["request"]["generationConfig"]["responseJsonSchema"]["title"] == "Decision"
