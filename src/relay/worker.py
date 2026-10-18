"""One isolated worker process per console stage. JSON is the entire IPC protocol."""

import json
import sys

import httpx
from redis.exceptions import RedisError

from relay.memory import Conflict, NotFound
from relay.runner import Runner


def main():
    tenant, incident, stage, provider = sys.argv[1:]
    runner = Runner(tenant)
    try:
        if stage == "resume":
            snapshot = runner.resume(incident, provider)
        else:
            method = {
                "first-shift": runner.first_shift,
                "guard-test": runner.guard_test,
                "reconcile": runner.reconcile,
                "initialize": runner.initialize,
            }[stage]
            snapshot = method(incident)
        print(json.dumps({"snapshot": snapshot}))
    except Exception as error:
        status = (
            409
            if isinstance(error, Conflict)
            else 404
            if isinstance(error, NotFound)
            else (
                422
                if isinstance(error, ValueError)
                else 503
                if isinstance(error, RedisError)
                else 502
                if isinstance(error, httpx.HTTPError)
                else 500
            )
        )
        print(json.dumps({"status": status, "detail": str(error)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
