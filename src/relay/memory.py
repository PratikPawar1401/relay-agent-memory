import json
import time
from typing import Any
from uuid import uuid4

from falkordb import FalkorDB

from relay import queries
from relay.config import Settings, sandbox_case, tenant_graph
from relay.evidence import Receipt


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


class Memory:
    """Tenant-scoped graph memory. Tenant routing is not user authentication."""

    def __init__(self, tenant: str, settings: Settings | None = None):
        self.tenant = tenant
        self.graph_name = tenant_graph(tenant)
        settings = settings or Settings.from_env()
        self.db = FalkorDB(host=settings.host, port=settings.port, socket_timeout=10)
        self.graph = self.db.select_graph(self.graph_name)

    def rows(self, query: str, **params: Any) -> list:
        return self.graph.query(query, params).result_set

    def guarded(self, query: str, **params: Any) -> dict:
        rows = self.rows(query, now=time.time(), **params)
        if not rows:
            raise Conflict(
                "Task is unavailable, claim expired, or evidence is not in this incident"
            )
        return rows[0][0]

    def create(self, title: str) -> dict:
        return self.rows(
            queries.CREATE_INCIDENT, incident=uuid4().hex, title=title, now=time.time()
        )[0][0]

    def incident(self, incident: str) -> dict:
        rows = self.rows(
            "MATCH (i:Incident {id:$incident}) RETURN properties(i)", incident=incident
        )
        if not rows:
            raise NotFound("Incident not found in this tenant")
        return rows[0][0]

    def claim(self, incident: str, agent: str, ttl: int = 300) -> dict:
        if not 1 <= ttl <= 3600:
            raise ValueError("Claim duration must be between 1 and 3600 seconds")
        self.incident(incident)
        return self.guarded(
            queries.CLAIM,
            incident=incident,
            agent=agent,
            token=uuid4().hex,
            expires=time.time() + ttl,
            event=uuid4().hex,
        )

    def append(
        self, incident: str, token: str, kind: str, content: str, payload: dict | None = None
    ) -> dict:
        payload = payload or {}
        verified = False
        verified_action = ""
        if kind == "health_verified":
            if payload.get("healthy") is not True or payload.get("service") != "checkout":
                raise ValueError("Resolution requires a positive checkout probe")
            verified_action = payload.get("action_id", "")
            matches = self.rows(
                "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(:Task)"
                "-[:HAS_ATTEMPT]->(a:Action {id:$action}) "
                "WHERE a.status <> 'running' RETURN a.id",
                incident=incident,
                action=verified_action,
            )
            if not matches:
                raise ValueError("Health evidence must reference a completed incident action")
            verified = True
        return self.guarded(
            queries.APPEND,
            incident=incident,
            token=token,
            event=uuid4().hex,
            kind=kind,
            content=content,
            payload=json.dumps(payload, sort_keys=True),
            verified=verified,
            verified_action=verified_action,
        )

    def hypothesize(
        self, incident: str, token: str, content: str, evidence: str, old: str | None = None
    ) -> dict:
        params = dict(
            incident=incident,
            token=token,
            content=content,
            evidence=evidence,
            hypothesis=uuid4().hex,
        )
        if old:
            params["old"] = old
        return self.guarded(queries.SUPERSEDE if old else queries.HYPOTHESIS, **params)

    def handoff(self, incident: str, token: str, content: str) -> dict:
        return self.guarded(
            queries.HANDOFF, incident=incident, token=token, content=content, event=uuid4().hex
        )

    def set_stage(self, incident: str, token: str, stage: str) -> dict:
        allowed = {
            "created",
            "first_shift_running",
            "handoff_ready",
            "successor_running",
            "action_running",
            "verifying",
            "uncertain",
            "resolved",
        }
        if stage not in allowed:
            raise ValueError("Unknown workflow stage")
        return self.guarded(
            "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(t:Task) "
            "WHERE t.token=$token AND t.status IN ['claimed','running'] "
            "SET t.stage=$stage RETURN properties(t)",
            incident=incident,
            token=token,
            stage=stage,
        )

    def start_action(self, incident: str, token: str, tool: str) -> dict:
        if tool not in {"restart_inventory", "restore_inventory_route"}:
            raise ValueError("Tool is not allowlisted")
        return self.guarded(
            queries.START_ACTION, incident=incident, token=token, tool=tool, action=uuid4().hex
        )

    def finish_action(self, incident: str, token: str, action: str, result: dict) -> dict:
        receipt = Receipt.model_validate(result)
        matches = self.rows(
            "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(:Task)"
            "-[:HAS_ATTEMPT]->(a:Action {id:$action}) RETURN a.tool",
            incident=incident,
            action=action,
        )
        if (
            receipt.operation != action
            or receipt.case != sandbox_case(self.tenant, incident)
            or not matches
            or receipt.tool != matches[0][0]
        ):
            raise ValueError("Receipt does not match the incident, operation and tool")
        healthy = receipt.healthy
        return self.guarded(
            queries.FINISH_ACTION,
            incident=incident,
            token=token,
            action=action,
            status="succeeded" if healthy else "failed",
            payload=json.dumps(result, sort_keys=True),
            content="Health recovered" if healthy else "Action did not restore service health",
            event=uuid4().hex,
            expires=time.time() + 300,
        )

    def resolve(self, incident: str, token: str, evidence: str) -> dict:
        return self.guarded(queries.RESOLVE, incident=incident, token=token, evidence=evidence)

    def link_evidence(self, incident: str, token: str, event: str, references: list[str]):
        """Persist provenance only between episodes belonging to the same incident."""
        return self.rows(
            "MATCH (i:Incident {id:$incident})-[:HAS_TASK]->(t:Task), "
            "(i)-[:HAS_EPISODE]->(e:Episode {id:$event}) "
            "WHERE t.status='claimed' AND t.token=$token AND t.expires_at>$now "
            "UNWIND $references AS reference "
            "MATCH (i)-[:HAS_EPISODE]->(source:Episode {id:reference}) "
            "MERGE (e)-[:CITES]->(source) RETURN source.id",
            incident=incident,
            token=token,
            event=event,
            references=list(dict.fromkeys(references)),
            now=time.time(),
        )

    def snapshot(self, incident: str) -> dict:
        info = self.incident(incident)
        task = self.rows(
            "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(t) RETURN properties(t)",
            incident=incident,
        )[0][0]
        # Claim credentials must not leak through read-only context endpoints.
        task.pop("token", None)
        episodes = [
            r[0]
            for r in self.rows(
                "MATCH (:Incident {id:$incident})-[:HAS_EPISODE]->(e) "
                "RETURN properties(e) ORDER BY e.created_at, e.id",
                incident=incident,
            )
        ]
        hypotheses = [
            r[0]
            for r in self.rows(
                "MATCH (:Incident {id:$incident})-[:HAS_HYPOTHESIS]->(h) "
                "RETURN properties(h) ORDER BY h.valid_from",
                incident=incident,
            )
        ]
        actions = [
            r[0]
            for r in self.rows(
                "MATCH (:Incident {id:$incident})-[:HAS_TASK]->(:Task)-[:HAS_ATTEMPT]->(a) "
                "RETURN properties(a) ORDER BY a.started_at",
                incident=incident,
            )
        ]
        for action in actions:
            action.pop("token", None)
        evidence = self.rows(
            "MATCH (:Incident {id:$incident})-[:HAS_EPISODE]->(e)-[r]->(h:Hypothesis) "
            "RETURN e.id, type(r), h.id",
            incident=incident,
        )
        failed = [r[0] for r in self.rows(queries.FAILED_ACTIONS, incident=incident)]
        for action in failed:
            action.pop("token", None)
        return {
            "tenant": self.tenant,
            "incident": info,
            "task": task,
            "episodes": episodes,
            "hypotheses": hypotheses,
            "actions": actions,
            "failed_actions": failed,
            "dependency_paths": [r[0] for r in self.rows(queries.DEPENDENCIES, incident=incident)],
            "procedures": [r[0] for r in self.rows(queries.PROCEDURES, incident=incident)],
            "evidence_links": [
                {"source": r[0], "relation": r[1], "target": r[2]} for r in evidence
            ],
        }
