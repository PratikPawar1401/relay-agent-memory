import json
import time
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from relay._vendor.cognee.retrieval import format_triplets, rank_candidates
from relay.api import app
from relay.memory import Conflict, NotFound
from relay.recall import retrieve
from relay.runner import Runner


def test_cognee_derived_rank_fusion_rewards_agreement_and_is_stable():
    candidates = [
        {"id": "single", "lexical_rank": 0, "graph_rank": None},
        {"id": "both", "lexical_rank": 1, "graph_rank": 0},
        {"id": "missing", "lexical_rank": None, "graph_rank": None},
    ]
    assert [x["id"] for x in rank_candidates(candidates, 3)] == ["both", "single"]
    assert rank_candidates(candidates, 0) == []
    assert "None" not in format_triplets(
        [
            {
                "source": {"name": "inventory", "missing": None},
                "target": {"name": "warehouse"},
                "attributes": {"relation": "DEPENDS_ON"},
            }
        ]
    )


@pytest.mark.integration
def test_stage_replay_and_early_guard_are_safe(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    with pytest.raises(Conflict, match="recorded failed restart"):
        runner.guard_test(incident)
    assert memory.snapshot(incident)["actions"] == []
    first = runner.first_shift(incident)
    assert first["task"]["stage"] == "handoff_ready"
    assert runner.first_shift(incident) == first
    guarded = runner.guard_test(incident)
    assert runner.guard_test(incident) == guarded
    assert sum(h["current"] for h in guarded["hypotheses"]) == 1


@pytest.mark.integration
@pytest.mark.parametrize("payload", [{}, {"route": "/wrong-stock"}])
def test_missing_configuration_never_dispatches(memory, monkeypatch, payload):
    incident = memory.create("Invalid configuration")["id"]
    token = memory.claim(incident, "audit")["token"]
    memory.append(incident, token, "configuration", "Missing fields", payload)
    runner = Runner(memory.tenant)
    monkeypatch.setattr(runner, "sandbox", lambda *_: pytest.fail("Tool must not dispatch"))
    with pytest.raises(ValueError):
        runner.act(incident, token, "restore_inventory_route")
    assert memory.snapshot(incident)["actions"] == []


@pytest.mark.integration
@pytest.mark.parametrize("change", ["precondition", "stale", "dependency"])
def test_graph_conditions_and_freshness_control_action(memory, monkeypatch, change):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    token = memory.claim(incident, "audit")["token"]
    config = runner.sandbox("/inspect", incident)
    if change == "stale":
        config["observed_at"] = time.time() - 301
    elif change == "precondition":
        memory.rows("MATCH (p:Procedure) SET p.precondition='Manual approval required'")
    else:
        memory.rows("MATCH (:Service {name:'checkout'})-[r:DEPENDS_ON]->() DELETE r")
    memory.append(incident, token, "configuration", "Configuration", config)
    monkeypatch.setattr(runner, "sandbox", lambda *_: pytest.fail("Tool must not dispatch"))
    with pytest.raises(Conflict):
        runner.act(incident, token, "restore_inventory_route")


@pytest.mark.integration
def test_transport_error_before_action_releases_claim(memory, monkeypatch):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]

    def offline(*_):
        raise httpx.ConnectError("Offline")

    monkeypatch.setattr(runner, "sandbox", offline)
    with pytest.raises(httpx.ConnectError):
        runner.first_shift(incident)
    assert memory.snapshot(incident)["task"]["status"] == "open"
    assert memory.snapshot(incident)["actions"] == []


@pytest.mark.integration
def test_reconcile_lost_response_uses_receipt_without_reexecution(memory, monkeypatch):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    original = runner.sandbox
    calls = []

    def lose_response(path, incident, body=None):
        result = original(path, incident, body)
        if path == "/actions":
            calls.append(body["operation"])
            raise httpx.ReadTimeout("Receipt saved, reply lost")
        return result

    monkeypatch.setattr(runner, "sandbox", lose_response)
    with pytest.raises(httpx.ReadTimeout):
        runner.first_shift(incident)
    assert memory.snapshot(incident)["task"]["status"] == "running"
    recovered = runner.reconcile(incident)
    assert recovered["task"]["status"] == "open"
    assert recovered["actions"][0]["status"] == "failed"
    assert len(calls) == 1
    assert runner.reconcile(incident) == recovered


@pytest.mark.integration
def test_reconcile_missing_receipt_does_not_release_or_execute(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    token = memory.claim(incident, "worker")["token"]
    memory.start_action(incident, token, "restart_inventory")
    with pytest.raises(Conflict, match="uncertain"):
        runner.reconcile(incident)
    assert memory.snapshot(incident)["task"]["status"] == "running"


@pytest.mark.integration
def test_false_health_and_wrong_receipt_rejected(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    token = memory.claim(incident, "worker")["token"]
    with pytest.raises(ValueError):
        memory.append(incident, token, "health_verified", "False", {"healthy": False})
    action = memory.start_action(incident, token, "restart_inventory")
    receipt = runner.sandbox(
        "/actions", incident, {"operation": action["id"], "tool": action["tool"]}
    )
    receipt["operation"] = uuid4().hex
    with pytest.raises(ValueError, match="does not match"):
        memory.finish_action(incident, token, action["id"], receipt)
    assert memory.snapshot(incident)["task"]["status"] == "running"


@pytest.mark.integration
def test_retrieval_pins_history_scopes_evidence_and_persists_actual_context(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    runner.first_shift(incident)
    other = memory.create("Unrelated secret fixture")["id"]
    other_token = memory.claim(other, "other")["token"]
    secret = memory.append(other, other_token, "observation", "inventory route recovery secret")
    result = runner.resume(incident)
    manifest_event = next(e for e in result["episodes"] if e["kind"] == "memory_retrieved")
    manifest = json.loads(manifest_event["payload"])
    selected = {e["id"] for e in manifest["selected"]}
    assert secret["id"] not in selected
    assert any(e["kind"] == "action_result" for e in manifest["selected"])
    assert manifest["context_bytes"] <= 18000
    assert manifest["triplets"]
    assert result["incident"]["status"] == "resolved"
    assert result["task"]["stage"] == "resolved"
    assert not any(h["current"] for h in result["hypotheses"])
    citations = memory.rows(
        "MATCH (:Episode {id:$id})-[:CITES]->(e) RETURN e.id", id=manifest_event["id"]
    )
    assert {r[0] for r in citations} == selected
    with pytest.raises(NotFound):
        retrieve(memory, uuid4().hex, "inventory")


@pytest.mark.integration
def test_console_uses_distinct_processes_and_recall_endpoint(memory):
    client = TestClient(app)
    snapshot = client.post("/v1/demo/start", json={"tenant": memory.tenant}).json()
    incident = snapshot["incident"]["id"]
    base = f"/v1/demo/{memory.tenant}/{incident}"
    assert client.post(base + "/first-shift").status_code == 200
    response = client.post(base + "/resume", json={"provider": "policy"})
    assert response.status_code == 200, response.text
    workers = [
        json.loads(e["payload"])
        for e in response.json()["episodes"]
        if e["kind"] == "worker_started"
    ]
    assert len({w["pid"] for w in workers}) == 2
    assert len({w["run_id"] for w in workers}) == 2
    recall = client.get(
        f"/v1/tenants/{memory.tenant}/incidents/{incident}/recall",
        params={"query": "failed restart"},
    )
    assert recall.status_code == 200
    assert recall.json()["manifest"]["selected"]
    # Replaying resolution is read-only and does not spawn another episode.
    assert client.post(base + "/resume", json={"provider": "policy"}).json() == response.json()
