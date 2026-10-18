import os
from uuid import uuid4

import httpx

from relay.config import Settings, sandbox_case
from relay.evidence import Configuration, applicable
from relay.memory import Conflict, Memory
from relay.models import Decision, decide
from relay.recall import retrieve


class Runner:
    def __init__(self, tenant: str, settings: Settings | None = None):
        self.settings = settings or Settings.from_env()
        self.memory = Memory(tenant, self.settings)
        self.tenant = tenant
        self.run_id = uuid4().hex

    def sandbox(self, path: str, incident: str, body: dict | None = None) -> dict:
        case = sandbox_case(self.tenant, incident)
        with httpx.Client(base_url=self.settings.sandbox_url, timeout=20) as client:
            response = (
                client.get(path, params={"case": case})
                if body is None
                else client.post(path, json={"case": case, **body})
            )
            if path != "/health" or response.status_code != 503:
                response.raise_for_status()
            return response.json()

    def create(self) -> dict:
        incident = self.memory.create("Checkout unavailable after inventory configuration change")
        try:
            self.initialize(incident["id"])
        except httpx.HTTPError as error:
            raise ValueError(
                f"Sandbox initialization failed; retry initialization for incident {incident['id']}"
            ) from error
        return incident

    def initialize(self, incident: str) -> dict:
        self.memory.incident(incident)
        self.sandbox("/cases", incident, {})
        return self.memory.snapshot(incident)

    def started(self, incident: str, token: str):
        self.memory.append(
            incident,
            token,
            "worker_started",
            "Independent worker session started",
            {
                "pid": os.getpid(),
                "run_id": self.run_id,
            },
        )

    def release_error(self, incident: str, token: str, error: Exception):
        # A running operation might already have executed: never release it on timeout.
        try:
            if self.memory.snapshot(incident)["task"]["status"] == "claimed":
                self.memory.append(
                    incident,
                    token,
                    "worker_error",
                    "Worker stopped before completion",
                    {
                        "error_type": type(error).__name__,
                        "run_id": self.run_id,
                    },
                )
                self.memory.handoff(
                    incident, token, "Worker stopped; inspect evidence before retrying."
                )
            elif self.memory.snapshot(incident)["task"]["status"] == "running":
                self.memory.set_stage(incident, token, "uncertain")
        except Exception:
            # Preserve the original error when the database/claim is unavailable too.
            pass

    def act(self, incident: str, token: str, tool: str) -> dict:
        context = self.memory.snapshot(incident)
        if tool in {a["tool"] for a in context["failed_actions"]}:
            raise Conflict("Shared memory blocks repeating a failed action for this incident")
        if tool == "restore_inventory_route":
            observations = [e for e in context["episodes"] if e["kind"] == "configuration"]
            if not observations:
                raise Conflict("No current configuration evidence")
            config = Configuration.model_validate_json(observations[-1].get("payload", "{}"))
            if not any(applicable(p, config) for p in context["procedures"]):
                raise Conflict("No graph procedure with a satisfied current precondition")
        action = self.memory.start_action(incident, token, tool)
        result = self.sandbox("/actions", incident, {"operation": action["id"], "tool": tool})
        return self.memory.finish_action(incident, token, action["id"], result)

    def first_shift(self, incident: str) -> dict:
        """Controlled fixture. Completed stages replay without new effects."""
        before = self.memory.snapshot(incident)
        if before["incident"]["status"] == "resolved":
            return before
        if any(a["tool"] == "restart_inventory" for a in before["actions"]):
            if before["task"]["status"] == "open":
                return before
            raise Conflict(
                "First shift already started; refresh or reconcile the existing operation"
            )
        token = self.memory.claim(incident, "investigator-1")["token"]
        try:
            self.memory.set_stage(incident, token, "first_shift_running")
            self.started(incident, token)
            health = self.sandbox("/health", incident)
            if health.get("healthy") is True:
                raise Conflict("Fixture is already healthy; initialize a fresh case")
            evidence = self.memory.append(
                incident, token, "observation", "Checkout is unavailable", health
            )
            current = next((h for h in before["hypotheses"] if h["current"]), None)
            self.memory.hypothesize(
                incident,
                token,
                "Inventory process may be stuck",
                evidence["id"],
                old=current["id"] if current else None,
            )
            self.act(incident, token, "restart_inventory")
            self.memory.set_stage(incident, token, "handoff_ready")
            self.memory.handoff(
                incident, token, "Restart failed. Inspect dependencies and configuration."
            )
            return self.memory.snapshot(incident)
        except Exception as error:
            self.release_error(incident, token, error)
            raise

    def guard_test(self, incident: str) -> dict:
        before = self.memory.snapshot(incident)
        if any(e["kind"] == "guard_rejection" for e in before["episodes"]):
            return before
        if not any(a["tool"] == "restart_inventory" for a in before["failed_actions"]):
            raise Conflict("A recorded failed restart is required before the guard test")
        token = self.memory.claim(incident, "guard-auditor")["token"]
        try:
            try:
                # Directly exercise the database guard; never dispatch a sandbox tool here.
                self.memory.start_action(incident, token, "restart_inventory")
            except Conflict as error:
                self.memory.append(
                    incident,
                    token,
                    "guard_rejection",
                    "Database rejected a repeated failed restart",
                    {
                        "tool": "restart_inventory",
                        "reason": str(error),
                        "controlled_test": True,
                        "failed_action_ids": [a["id"] for a in before["failed_actions"]],
                    },
                )
                self.memory.handoff(incident, token, "Guard verified; successor may continue.")
                return self.memory.snapshot(incident)
            raise RuntimeError("Database guard invariant failed; no external tool was dispatched")
        except Exception as error:
            self.release_error(incident, token, error)
            raise

    def verify(self, incident: str, token: str, action: dict):
        health = self.sandbox("/health", incident)
        if health.get("healthy") is True:
            verified = self.memory.append(
                incident,
                token,
                "health_verified",
                "Independent checkout HTTP probe passed",
                {
                    **health,
                    "action_id": action["id"],
                },
            )
            self.memory.resolve(incident, token, verified["id"])
        else:
            self.memory.handoff(
                incident, token, "Recovery verification failed; investigate further."
            )

    def resume(self, incident: str, provider: str = "policy") -> dict:
        before = self.memory.snapshot(incident)
        if before["incident"]["status"] == "resolved":
            return before
        if "restart_inventory" not in {a["tool"] for a in before["failed_actions"]}:
            raise Conflict("Run the controlled first shift before the successor demo")
        token = self.memory.claim(incident, "successor-2")["token"]
        try:
            self.memory.set_stage(incident, token, "successor_running")
            self.started(incident, token)
            # A prior repair may have completed before its final verification was interrupted.
            repaired = next(
                (
                    a
                    for a in reversed(before["actions"])
                    if a["tool"] == "restore_inventory_route" and a["status"] == "succeeded"
                ),
                None,
            )
            if repaired:
                self.verify(incident, token, repaired)
                return self.memory.snapshot(incident)
            config = Configuration.model_validate(self.sandbox("/inspect", incident))
            evidence = self.memory.append(
                incident, token, "configuration", "Inventory route inspected", config.model_dump()
            )
            old = next((h for h in before["hypotheses"] if h["current"]), None)
            corrected = "Inventory points to an invalid warehouse route"
            if config.route != config.expected_route and (
                old is None or old["content"] != corrected
            ):
                self.memory.hypothesize(
                    incident, token, corrected, evidence["id"], old=old["id"] if old else None
                )
            recalled = retrieve(
                self.memory,
                incident,
                "inventory route recovery failed restart current configuration procedure",
            )
            manifest = self.memory.append(
                incident,
                token,
                "memory_retrieved",
                "Successor retrieved bounded Cognee-derived graph context",
                {
                    **recalled["manifest"],
                    "pid": os.getpid(),
                    "run_id": self.run_id,
                },
            )
            self.memory.link_evidence(
                incident, token, manifest["id"], [e["id"] for e in recalled["context"]["episodes"]]
            )
            context = recalled["context"]
            if provider == "policy":
                decision = Decision(
                    tool="restore_inventory_route",
                    reason="Controlled policy: applicable graph procedure and current configuration",
                    evidence_ids=[evidence["id"]],
                )
                metadata = {"provider": "policy", "model": None, "usage": {}}
            else:
                decision, metadata = decide(context, provider)
            known = {e["id"]: e for e in context["episodes"]}
            if len(set(decision.evidence_ids)) != len(decision.evidence_ids) or not set(
                decision.evidence_ids
            ).issubset(known):
                raise ValueError("Citations must be unique IDs from the retrieved evidence")
            if (
                decision.tool == "restore_inventory_route"
                and evidence["id"] not in decision.evidence_ids
            ):
                raise ValueError("A repair decision must cite the current configuration evidence")
            event = self.memory.append(
                incident,
                token,
                "decision",
                decision.reason,
                {
                    **decision.model_dump(),
                    **metadata,
                    "retrieval_id": manifest["id"],
                },
            )
            self.memory.link_evidence(incident, token, event["id"], decision.evidence_ids)
            if decision.tool == "handoff":
                self.memory.handoff(incident, token, decision.reason)
                return self.memory.snapshot(incident)
            action = self.act(incident, token, decision.tool)
            self.verify(incident, token, action)
            return self.memory.snapshot(incident)
        except Exception as error:
            self.release_error(incident, token, error)
            raise

    def reconcile(self, incident: str) -> dict:
        """Read an existing durable receipt. Never resend an external operation."""
        rows = self.memory.rows(
            "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(t:Task)-[:HAS_ATTEMPT]->(a:Action) "
            "WHERE t.status='running' AND a.status='running' RETURN t.token, properties(a)",
            incident=incident,
        )
        if not rows:
            return self.memory.snapshot(incident)
        token, action = rows[0]
        with httpx.Client(base_url=self.settings.sandbox_url, timeout=20) as client:
            response = client.get(
                "/operations",
                params={"case": sandbox_case(self.tenant, incident), "operation": action["id"]},
            )
            if response.status_code in {404, 409}:
                raise Conflict(
                    "No completed receipt. Execution remains uncertain; inspect the sandbox manually. No retry was dispatched."
                )
            response.raise_for_status()
            receipt = response.json()
        completed = self.memory.finish_action(incident, token, action["id"], receipt)
        self.memory.append(
            incident,
            token,
            "reconciled",
            "Recovered matching durable sandbox receipt",
            {"operation": action["id"]},
        )
        if action["tool"] == "restore_inventory_route":
            self.verify(incident, token, completed)
        else:
            self.memory.handoff(
                incident, token, "Reconciled failed attempt; successor may continue."
            )
        return self.memory.snapshot(incident)
