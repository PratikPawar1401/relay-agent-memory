import json
import os
import subprocess
import sys
from typing import Literal
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from relay.memory import Conflict, Memory, NotFound
from relay.recall import retrieve
from relay.runner import Runner


def web_origins() -> list[str]:
    configured = os.getenv("RELAY_WEB_ORIGINS")
    if configured:
        return [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    return [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]


app = FastAPI(
    title="Relay memory API",
    version="0.1.0",
    description="Local developer API. Tenant routing is not authentication.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=web_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class NewIncident(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class Claim(BaseModel):
    agent: str = Field(min_length=1, max_length=100)
    ttl: int = Field(default=300, ge=1, le=3600)


class Handoff(BaseModel):
    token: str = Field(min_length=32, max_length=32)
    summary: str = Field(min_length=1, max_length=4000)


class DemoStart(BaseModel):
    tenant: str | None = Field(default=None, min_length=1, max_length=64)


class DemoResume(BaseModel):
    provider: Literal["policy", "ollama", "gemini"] = "policy"


@app.exception_handler(NotFound)
def missing(_request: Request, _error: NotFound):
    return JSONResponse(status_code=404, content={"detail": "Incident not found in this tenant"})


@app.exception_handler(Conflict)
def conflict(_request: Request, error: Conflict):
    return JSONResponse(status_code=409, content={"detail": str(error)})


@app.exception_handler(ValueError)
def invalid(_request: Request, error: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(error)})


@app.exception_handler(RedisError)
def unavailable(_request: Request, _error: RedisError):
    return JSONResponse(
        status_code=503, content={"detail": "Graph database unavailable; no fallback memory"}
    )


@app.get("/health")
def health():
    Memory("health").rows("RETURN 1")
    return {"status": "ok", "memory": "falkordb"}


@app.post("/v1/demo/start", status_code=201)
def demo_start(body: DemoStart):
    """Create the synthetic incident without running either agent shift."""
    tenant = body.tenant or f"demo-{uuid4().hex[:12]}"
    runner = Runner(tenant)
    incident = runner.create()
    return runner.memory.snapshot(incident["id"])


@app.post("/v1/demo/{tenant}/{incident}/first-shift")
def demo_first_shift(tenant: str, incident: str):
    return run_worker(tenant, incident, "first-shift")


@app.post("/v1/demo/{tenant}/{incident}/guard-test")
def demo_guard_test(tenant: str, incident: str):
    return run_worker(tenant, incident, "guard-test")


@app.post("/v1/demo/{tenant}/{incident}/resume")
def demo_resume(tenant: str, incident: str, body: DemoResume):
    return run_worker(tenant, incident, "resume", body.provider)


def run_worker(tenant: str, incident: str, stage: str, provider: str = "policy"):
    Memory(tenant).incident(incident)
    try:
        process = subprocess.run(
            [sys.executable, "-m", "relay.worker", tenant, incident, stage, provider],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired as error:
        raise HTTPException(
            504, "Worker timed out. Refresh state; reconcile a running operation before retrying."
        ) from error
    try:
        result = json.loads(process.stdout)
    except ValueError as error:
        raise HTTPException(
            502, "Worker stopped without a result. Refresh persisted state."
        ) from error
    if "snapshot" not in result:
        raise HTTPException(result.get("status", 500), result.get("detail", "Worker failed"))
    return result["snapshot"]


@app.post("/v1/demo/{tenant}/{incident}/reconcile")
def demo_reconcile(tenant: str, incident: str):
    return run_worker(tenant, incident, "reconcile")


@app.post("/v1/demo/{tenant}/{incident}/initialize")
def demo_initialize(tenant: str, incident: str):
    return run_worker(tenant, incident, "initialize")


@app.get("/v1/tenants/{tenant}/incidents/{incident}/recall")
def recall(tenant: str, incident: str, query: str = Query(min_length=1, max_length=500)):
    return retrieve(Memory(tenant), incident, query)


@app.get("/v1/providers")
def providers():
    local_model = os.getenv("RELAY_OLLAMA_MODEL", "mistral:latest")
    available = False
    try:
        response = httpx.get(
            os.getenv("RELAY_OLLAMA_URL", "http://127.0.0.1:11434") + "/api/tags", timeout=2
        )
        response.raise_for_status()
        available = any(m.get("name") == local_model for m in response.json().get("models", []))
    except (httpx.HTTPError, ValueError):
        pass
    return {
        "policy": True,
        "ollama": available,
        "gemini": bool(os.getenv("GEMINI_API_KEY") and os.getenv("RELAY_GEMINI_MODEL")),
        "local_model": local_model,
    }


@app.post("/v1/tenants/{tenant}/incidents", status_code=201)
def create(tenant: str, body: NewIncident):
    return Memory(tenant).create(body.title)


@app.get("/v1/tenants/{tenant}/incidents/{incident}")
def context(tenant: str, incident: str):
    return Memory(tenant).snapshot(incident)


@app.post("/v1/tenants/{tenant}/incidents/{incident}/claim")
def claim(tenant: str, incident: str, body: Claim):
    return Memory(tenant).claim(incident, body.agent, body.ttl)


@app.post("/v1/tenants/{tenant}/incidents/{incident}/handoff")
def handoff(tenant: str, incident: str, body: Handoff):
    return Memory(tenant).handoff(incident, body.token, body.summary)
