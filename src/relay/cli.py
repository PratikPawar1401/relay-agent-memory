import argparse
import asyncio
import json
import subprocess
import sys
from uuid import uuid4

from relay.memory import Memory
from relay.runner import Runner


def main():
    parser = argparse.ArgumentParser(description="Relay local incident-memory demo")
    parser.add_argument(
        "command",
        choices=[
            "demo",
            "create",
            "first-shift",
            "resume",
            "context",
            "recall",
            "reconcile",
            "guard-test",
            "initialize",
            "evaluate",
            "graphiti-probe",
            "graphiti-sync",
            "graphiti-search",
        ],
    )
    parser.add_argument("--tenant", default="demo")
    parser.add_argument("--incident")
    parser.add_argument("--query")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--provider", choices=["policy", "ollama", "gemini"], default="policy")
    args = parser.parse_args()
    try:
        if args.command == "evaluate":
            from relay.evaluation import evaluate

            print(json.dumps(evaluate(args.provider, args.runs), indent=2))
            return
        if args.command.startswith("graphiti-"):
            from relay import graphiti_bridge

            if args.command == "graphiti-probe":
                result = asyncio.run(graphiti_bridge.probe(args.tenant))
            elif args.command == "graphiti-sync":
                if not args.incident:
                    parser.error("--incident is required")
                result = asyncio.run(graphiti_bridge.sync(args.tenant, args.incident))
            else:
                if not args.query:
                    parser.error("--query is required")
                result = asyncio.run(graphiti_bridge.search(args.tenant, args.query))
            print(json.dumps(result, indent=2))
            return
        if args.command == "demo":
            tenant = f"demo-{uuid4().hex[:12]}"
            created = subprocess.run(
                [sys.executable, "-m", "relay.cli", "create", "--tenant", tenant],
                capture_output=True,
                text=True,
                check=True,
            )
            incident = json.loads(created.stdout)["id"]
            for phase in ("first-shift", "resume"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "relay.cli",
                        phase,
                        "--tenant",
                        tenant,
                        "--incident",
                        incident,
                        "--provider",
                        args.provider,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                snapshot = json.loads(result.stdout)
                print(
                    json.dumps(
                        {
                            "phase": phase,
                            "tenant": tenant,
                            "incident": incident,
                            "provider": "controlled fixture"
                            if phase == "first-shift"
                            else args.provider,
                            "status": snapshot["incident"]["status"],
                            "actions": snapshot["actions"],
                            "hypotheses": snapshot["hypotheses"],
                        },
                        indent=2,
                    )
                )
            print(f"\nInspect: relay context --tenant {tenant} --incident {incident}")
            if snapshot["incident"]["status"] != "resolved":
                raise RuntimeError("Successor handed off without resolving the incident")
            return
        runner = Runner(args.tenant)
        if args.command == "create":
            result = runner.create()
        else:
            if not args.incident:
                parser.error("--incident is required")
            if args.command == "first-shift":
                result = runner.first_shift(args.incident)
            elif args.command == "resume":
                result = runner.resume(args.incident, args.provider)
            elif args.command == "guard-test":
                result = runner.guard_test(args.incident)
            elif args.command == "reconcile":
                result = runner.reconcile(args.incident)
            elif args.command == "initialize":
                result = runner.initialize(args.incident)
            elif args.command == "recall":
                from relay.recall import retrieve

                result = retrieve(
                    runner.memory, args.incident, args.query or "inventory failed restart recovery"
                )
            else:
                result = Memory(args.tenant).snapshot(args.incident)
        print(json.dumps(result, indent=2))
    except subprocess.CalledProcessError as error:
        print(error.stderr, file=sys.stderr)
        raise SystemExit(1) from None
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
