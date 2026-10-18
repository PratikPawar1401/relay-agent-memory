import hashlib
import os
import re
from dataclasses import dataclass


def tenant_graph(tenant: str, namespace: str = "memory") -> str:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", tenant):
        raise ValueError("Tenant must be 1–64 letters, numbers, underscores or hyphens")
    if namespace not in {"memory", "graphiti"}:
        raise ValueError("Unknown graph namespace")
    # Hashing prevents tenant names becoming Cypher identifiers or ambiguous graph keys.
    return f"relay{namespace}{hashlib.sha256(tenant.encode()).hexdigest()}"


def sandbox_case(tenant: str, incident: str) -> str:
    return hashlib.sha256(f"{tenant}\0{incident}".encode()).hexdigest()


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 6380
    sandbox_url: str = "http://127.0.0.1:8091"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            host=os.getenv("RELAY_DB_HOST", "127.0.0.1"),
            port=int(os.getenv("RELAY_DB_PORT", "6380")),
            sandbox_url=os.getenv("RELAY_SANDBOX_URL", "http://127.0.0.1:8091"),
        )
