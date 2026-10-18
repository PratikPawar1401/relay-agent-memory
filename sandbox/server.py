"""Local-only synthetic incident sandbox; no third-party dependencies.

Checkout calls an inventory subprocess, which calls a warehouse HTTP endpoint.
Each case starts with a bad inventory route. Restarting the subprocess does not
repair persisted configuration. Restoring /stock does. SQLite stores ONLY the
fixture's configuration and tool receipts, never the agent's memory.
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = os.getenv("SANDBOX_DB", "/data/sandbox.sqlite")
MUTATION_LOCK = threading.Lock()
inventory = None


def connect():
    return sqlite3.connect(DB, timeout=10)


def request_json(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)
    except (urllib.error.URLError, TimeoutError):
        return 503, {"healthy": False, "error": "dependency unreachable"}


def start_inventory():
    global inventory
    inventory = subprocess.Popen([sys.executable, __file__, "inventory"])
    for _ in range(50):
        if request_json("http://127.0.0.1:8092/ready")[0] == 200:
            return
        time.sleep(0.05)
    raise RuntimeError("Inventory process failed to start")


class Handler(BaseHTTPRequestHandler):
    role = "manager"

    def log_message(self, *_args):
        pass

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/ready":
            return self.reply(200, {"ready": True, "role": self.role})
        if self.role == "warehouse":
            status = 200 if parsed.path == "/stock" else 404
            return self.reply(status, {"healthy": status == 200, "service": "warehouse"})
        case = urllib.parse.parse_qs(parsed.query).get("case", [""])[0]
        with connect() as db:
            row = db.execute("SELECT route FROM cases WHERE id=?", (case,)).fetchone()
        if not row:
            return self.reply(404, {"error": "Unknown sandbox case"})
        if parsed.path == "/operations" and self.role == "manager":
            operation = urllib.parse.parse_qs(parsed.query).get("operation", [""])[0]
            with connect() as db:
                saved = db.execute(
                    "SELECT receipt FROM operations WHERE id=? AND case_id=?", (operation, case)
                ).fetchone()
            if not saved:
                return self.reply(404, {"error": "No receipt; execution remains uncertain"})
            if saved[0] is None:
                return self.reply(
                    409, {"error": "Incomplete reservation; manual inspection required"}
                )
            return self.reply(200, json.loads(saved[0]))
        if self.role == "inventory":
            status, result = request_json(f"http://127.0.0.1:8093{row[0]}")
            return self.reply(
                200 if status == 200 else 503,
                {"healthy": status == 200, "service": "inventory", "upstream": result},
            )
        if parsed.path == "/inspect":
            return self.reply(
                200,
                {
                    "service": "inventory",
                    "route": row[0],
                    "expected_route": "/stock",
                    "source": "sandbox configuration",
                    "observed_at": time.time(),
                },
            )
        if parsed.path == "/health":
            status, result = request_json(f"http://127.0.0.1:8092/health?case={case}")
            return self.reply(
                200 if status == 200 else 503,
                {"healthy": status == 200, "service": "checkout", "dependency": result},
            )
        self.reply(404, {"error": "Unknown route"})

    def do_POST(self):
        if self.role != "manager":
            return self.reply(405, {"error": "Read-only service"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 16384:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length))
            case = data["case"]
            if not isinstance(case, str) or not re.fullmatch(r"[a-f0-9]{64}", case):
                raise ValueError("Invalid case")
            if self.path == "/cases":
                with connect() as db:
                    db.execute("INSERT OR IGNORE INTO cases VALUES (?, ?)", (case, "/wrong-stock"))
                return self.reply(201, {"case": case})
            if self.path != "/actions":
                return self.reply(404, {"error": "Unknown route"})
            operation, tool = data["operation"], data["tool"]
            if tool not in {"restart_inventory", "restore_inventory_route"}:
                raise ValueError("Unknown tool")
            if not isinstance(operation, str) or not re.fullmatch(r"[a-f0-9]{32}", operation):
                raise ValueError("Invalid operation")
            with MUTATION_LOCK:
                with connect() as db:
                    if not db.execute("SELECT 1 FROM cases WHERE id=?", (case,)).fetchone():
                        return self.reply(404, {"error": "Unknown case"})
                    prior = db.execute(
                        "SELECT tool, receipt FROM operations WHERE id=? AND case_id=?",
                        (operation, case),
                    ).fetchone()
                    if prior:
                        if prior[0] != tool:
                            return self.reply(
                                409, {"error": "Operation ID reused with different tool"}
                            )
                        if prior[1] is None:
                            return self.reply(
                                409, {"error": "Uncertain prior execution; inspect manually"}
                            )
                        return self.reply(200, json.loads(prior[1]))
                    db.execute(
                        "INSERT INTO operations VALUES (?, ?, ?, NULL)", (operation, case, tool)
                    )
                # Receipt reservation is durable before the external effect. An interrupted
                # operation is not automatically retried: it may already have executed.
                if tool == "restart_inventory":
                    inventory.terminate()
                    inventory.wait(timeout=5)
                    start_inventory()
                else:
                    with connect() as db:
                        db.execute("UPDATE cases SET route='/stock' WHERE id=?", (case,))
                status, health = request_json(f"http://127.0.0.1:8092/health?case={case}")
                receipt = {
                    "operation": operation,
                    "case": case,
                    "tool": tool,
                    "healthy": status == 200,
                    "health": health,
                    "synthetic_environment": True,
                }
                with connect() as db:
                    db.execute(
                        "UPDATE operations SET receipt=? WHERE id=? AND case_id=?",
                        (json.dumps(receipt), operation, case),
                    )
                return self.reply(200, receipt)
        except (ValueError, KeyError, TypeError):
            self.reply(400, {"error": "Invalid sandbox request"})


def serve(role, port):
    handler = type(f"{role}Handler", (Handler,), {"role": role})
    ThreadingHTTPServer(
        ("0.0.0.0" if role == "manager" else "127.0.0.1", port), handler
    ).serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        serve("inventory", 8092)
    else:
        with connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, route TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS operations "
                "(id TEXT, case_id TEXT, tool TEXT NOT NULL, receipt TEXT, PRIMARY KEY(id,case_id))"
            )
        threading.Thread(target=serve, args=("warehouse", 8093), daemon=True).start()
        start_inventory()
        try:
            serve("manager", 8091)
        finally:
            inventory.terminate()
            inventory.wait(timeout=5)
