import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from relay.api import app
from relay.config import sandbox_case
from relay.memory import Conflict, Memory, NotFound
from relay.runner import Runner

pytestmark = pytest.mark.integration


def contender(tenant, incident, n):
    try:
        return Memory(tenant).claim(incident, f"worker-{n}")
    except Conflict:
        return None


def test_only_one_of_eight_processes_claims_task(memory):
    incident = memory.create("Race")["id"]
    with ProcessPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(contender, memory.tenant, incident, n) for n in range(8)]
        winners = [result for future in futures if (result := future.result()) is not None]
    assert len(winners) == 1
    assert memory.snapshot(incident)["task"]["generation"] == 1


def test_stale_owner_cannot_write_after_handoff(memory):
    incident = memory.create("Handoff")["id"]
    first = memory.claim(incident, "first")["token"]
    memory.handoff(incident, first, "Continue investigation")
    second = memory.claim(incident, "second")["token"]
    with pytest.raises(Conflict):
        memory.append(incident, first, "observation", "stale write")
    memory.append(incident, second, "observation", "valid write")
    assert "token" not in memory.snapshot(incident)["task"]


def test_expired_claim_can_be_reclaimed_but_running_action_cannot(memory):
    incident = memory.create("Expiry")["id"]
    old = memory.claim(incident, "old")["token"]
    # Force expiry in the fixture rather than introducing clock-sensitive sleeps.
    memory.rows("MATCH (t:Task {id:$incident}) SET t.expires_at=0", incident=incident)
    new = memory.claim(incident, "new")["token"]
    with pytest.raises(Conflict):
        memory.start_action(incident, old, "restart_inventory")
    memory.start_action(incident, new, "restart_inventory")
    memory.rows("MATCH (t:Task {id:$incident}) SET t.expires_at=0", incident=incident)
    with pytest.raises(Conflict):
        memory.claim(incident, "third")


def test_temporal_update_keeps_old_fact_and_provenance(memory):
    incident = memory.create("Temporal")["id"]
    token = memory.claim(incident, "worker")["token"]
    first = memory.append(incident, token, "observation", "Initial evidence")
    old = memory.hypothesize(incident, token, "Initial hypothesis", first["id"])
    second = memory.append(incident, token, "observation", "Contradictory evidence")
    memory.hypothesize(incident, token, "Corrected hypothesis", second["id"], old["id"])
    context = memory.snapshot(incident)
    assert len(context["hypotheses"]) == 2
    assert sum(h["current"] for h in context["hypotheses"]) == 1
    assert context["hypotheses"][0]["valid_until"] >= old["valid_from"]
    assert {link["relation"] for link in context["evidence_links"]} == {"SUPPORTS", "CONTRADICTS"}


def test_tenants_and_incident_evidence_are_isolated(memory):
    incident = memory.create("Private synthetic incident")["id"]
    token = memory.claim(incident, "worker")["token"]
    event = memory.append(incident, token, "observation", "Tenant-only evidence")
    other = Memory("test-" + uuid4().hex)
    try:
        with pytest.raises(NotFound):
            other.snapshot(incident)
        second = memory.create("Other incident")["id"]
        second_token = memory.claim(second, "worker2")["token"]
        with pytest.raises(Conflict):
            memory.hypothesize(second, second_token, "Cross-incident injection", event["id"])
    finally:
        if other.graph_name in other.db.list_graphs():
            other.graph.delete()


def test_failed_action_rejected_inside_database_guard(memory):
    incident = memory.create("Deduplication")["id"]
    token = memory.claim(incident, "worker")["token"]
    action = memory.start_action(incident, token, "restart_inventory")
    memory.finish_action(
        incident,
        token,
        action["id"],
        {
            "healthy": False,
            "operation": action["id"],
            "tool": "restart_inventory",
            "case": sandbox_case(memory.tenant, incident),
            "health": {"healthy": False},
            "synthetic_environment": True,
        },
    )
    with pytest.raises(Conflict):
        memory.start_action(incident, token, "restart_inventory")


def test_full_demo_across_processes_with_real_http_recovery(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    assert runner.sandbox("/health", incident)["healthy"] is False
    for phase in ("first-shift", "resume"):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "relay.cli",
                phase,
                "--tenant",
                memory.tenant,
                "--incident",
                incident,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        context = json.loads(process.stdout)
        if phase == "first-shift":
            assert context["task"]["status"] == "open"
            assert context["actions"][0]["status"] == "failed"
    assert context["incident"]["status"] == "resolved"
    assert [a["tool"] for a in context["actions"]] == [
        "restart_inventory",
        "restore_inventory_route",
    ]
    assert runner.sandbox("/health", incident)["healthy"] is True
    assert ["checkout", "inventory", "warehouse"] in context["dependency_paths"]


def test_sandbox_tool_receipts_are_idempotent(memory):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    operation = uuid4().hex
    body = {"operation": operation, "tool": "restart_inventory"}
    first = runner.sandbox("/actions", incident, body)
    second = runner.sandbox("/actions", incident, body)
    assert first == second
    assert first["healthy"] is False


def test_model_failure_releases_claim_without_action(memory, monkeypatch):
    runner = Runner(memory.tenant)
    incident = runner.create()["id"]
    runner.first_shift(incident)

    def bad_model(*_args):
        raise ValueError("Invalid model output")

    monkeypatch.setattr("relay.runner.decide", bad_model)
    with pytest.raises(ValueError, match="Invalid model"):
        runner.resume(incident, "ollama")
    snapshot = memory.snapshot(incident)
    assert snapshot["task"]["status"] == "open"
    assert len(snapshot["actions"]) == 1


def test_local_api_claim_conflict_and_context(memory):
    client = TestClient(app)
    base = f"/v1/tenants/{memory.tenant}/incidents"
    created = client.post(base, json={"title": "API incident"})
    assert created.status_code == 201
    path = f"{base}/{created.json()['id']}"
    first = client.post(path + "/claim", json={"agent": "first"})
    assert first.status_code == 200
    assert client.post(path + "/claim", json={"agent": "second"}).status_code == 409
    assert "token" not in client.get(path).json()["task"]
    assert (
        client.post(
            path + "/handoff", json={"token": first.json()["token"], "summary": "Continue"}
        ).status_code
        == 200
    )
    assert client.post("/v1/tenants/bad!tenant/incidents", json={"title": "Bad"}).status_code == 422


def test_staged_demo_api_exposes_guard_and_successor_evidence(memory):
    client = TestClient(app)
    started = client.post("/v1/demo/start", json={"tenant": memory.tenant})
    assert started.status_code == 201
    incident = started.json()["incident"]["id"]
    base = f"/v1/demo/{memory.tenant}/{incident}"

    first = client.post(base + "/first-shift")
    assert first.status_code == 200
    assert first.json()["actions"][0]["status"] == "failed"

    guard = client.post(base + "/guard-test")
    assert guard.status_code == 200
    rejection = [e for e in guard.json()["episodes"] if e["kind"] == "guard_rejection"]
    assert rejection and json.loads(rejection[0]["payload"])["controlled_test"] is True

    resumed = client.post(base + "/resume", json={"provider": "policy"})
    assert resumed.status_code == 200
    assert resumed.json()["incident"]["status"] == "resolved"


def test_api_fails_closed_without_database(monkeypatch):
    monkeypatch.setenv("RELAY_DB_PORT", "1")
    response = TestClient(app).get("/health")
    assert response.status_code == 503
    assert "no fallback" in response.json()["detail"]


def test_uncertain_tool_delivery_is_not_automatically_reclaimed(memory, monkeypatch):
    runner = Runner(memory.tenant)
    incident = memory.create("Uncertain tool delivery")["id"]
    token = memory.claim(incident, "worker")["token"]

    def interrupted(*_args, **_kwargs):
        raise httpx.ReadTimeout("Response lost after possible execution")

    monkeypatch.setattr(runner, "sandbox", interrupted)
    with pytest.raises(httpx.ReadTimeout):
        runner.act(incident, token, "restart_inventory")
    snapshot = memory.snapshot(incident)
    assert snapshot["task"]["status"] == "running"
    assert snapshot["actions"][0]["status"] == "running"
    with pytest.raises(Conflict):
        memory.claim(incident, "replacement")
