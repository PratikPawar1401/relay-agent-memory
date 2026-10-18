# Deploying Relay with Vercel

Vercel hosts the Relay React console. The FastAPI API, FalkorDB, and synthetic sandbox remain on a persistent backend host.

This split is required by the current runtime: the API launches Python worker subprocesses, FalkorDB needs durable storage, and the sandbox keeps SQLite receipts plus a live inventory subprocess. Moving those pieces into Vercel Functions would change the product rather than deploy it unchanged.

## 1. Deploy the backend

Run the existing Docker Compose stack on a reachable Linux host, VM, or container platform with persistent volumes:

```sh
docker compose up -d --wait
uv sync --locked
uv run uvicorn relay.api:app --host 0.0.0.0 --port 8088
```

Do not expose FalkorDB or the sandbox directly to the public internet. Expose only the API through HTTPS, preferably behind a reverse proxy with TLS, request limits, and authentication.

Set these backend variables:

```text
RELAY_WEB_ORIGINS=https://your-project.vercel.app,https://your-production-domain.example
RELAY_DB_HOST=127.0.0.1
RELAY_DB_PORT=6380
RELAY_SANDBOX_URL=http://127.0.0.1:8091
```

Use the actual internal service addresses for the host layout. The API must be able to reach FalkorDB and the sandbox from the backend machine.

## 2. Deploy the console

Create a Vercel project from the repository root. The checked-in `vercel.json` installs and builds the frontend from `frontend/` and serves `frontend/dist`.

Set this Vercel environment variable for Production, Preview, and Development as appropriate:

```text
VITE_RELAY_API=https://api.your-domain.example
```

Then deploy:

```sh
vercel
vercel --prod
```

The frontend API URL is compiled into the browser bundle. It must be an HTTPS URL reachable by the user's browser; `127.0.0.1` only works for local development.

## 3. Minimum public-demo hardening

Before sharing the URL:

- Add API authentication and derive tenant scope from the authenticated identity.
- Restrict CORS to the exact Vercel production domain, not `*`.
- Keep FalkorDB, the sandbox, and model credentials private.
- Add a read-only demo tenant or reset mechanism so one visitor cannot corrupt another visitor's run.
- Configure API timeouts and a visible recovery path for a lost mutation response.
- Confirm the API health endpoint and a complete deterministic run from a clean browser.

The current local policy provider is the reliable public demo path. Ollama is local to the backend host, and Gemini requires credentials on the API process; neither should be assumed available from Vercel.

## Architecture boundary

```text
Browser -> Vercel static React app -> HTTPS FastAPI API
                                      |-> FalkorDB with persistent volume
                                      |-> sandbox with persistent receipts
                                      |-> optional model provider
```

Vercel deployment makes the console publicly reachable. It does not, by itself, make Relay a multi-tenant production service. Authentication, authorization, durable recovery, and isolated runtime effects remain backend work.
