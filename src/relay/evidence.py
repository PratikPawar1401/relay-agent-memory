"""Typed evidence contracts at the operational memory boundary."""

import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PRECONDITION = "inventory route differs from /stock"


class Configuration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Literal["inventory"]
    route: str = Field(min_length=1, max_length=200)
    expected_route: Literal["/stock"]
    source: Literal["sandbox configuration"]
    observed_at: float

    def is_fresh(self) -> bool:
        return 0 <= time.time() - self.observed_at <= 300


class Receipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation: str = Field(pattern=r"^[a-f0-9]{32}$")
    case: str = Field(pattern=r"^[a-f0-9]{64}$")
    tool: Literal["restart_inventory", "restore_inventory_route"]
    healthy: bool
    health: dict
    synthetic_environment: Literal[True]


def applicable(procedure: dict, configuration: Configuration) -> bool:
    return (
        procedure.get("name") == "restore_inventory_route"
        and procedure.get("precondition") == PRECONDITION
        and procedure.get("target") == configuration.service
        and configuration.is_fresh()
        and configuration.route != configuration.expected_route
    )
