import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import type { Action, Dictionary, Episode, Hypothesis, Provider, Snapshot } from "./types";
import "./styles.css";

const API = import.meta.env.VITE_RELAY_API ?? "http://127.0.0.1:8088";

function parsePayload(value?: string): Dictionary {
  if (!value) return {};
  try {
    return JSON.parse(value) as Dictionary;
  } catch {
    return {};
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    signal: AbortSignal.timeout(190000),
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? `Request failed (${response.status})`));
  }
  return response.json() as Promise<T>;
}

function Icon({ name }: { name: "bolt" | "memory" | "shield" | "graph" | "check" | "arrow" }) {
  const paths = {
    bolt: "M13 2 4 14h7l-1 8 9-12h-7z",
    memory: "M7 3v3M12 3v3M17 3v3M7 18v3M12 18v3M17 18v3M3 7h3M3 12h3M3 17h3M18 7h3M18 12h3M18 17h3M7 6h10a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Z",
    shield: "M12 3 4.5 6v5.5c0 4.6 3.2 7.9 7.5 9.5 4.3-1.6 7.5-4.9 7.5-9.5V6zM9 12l2 2 4-4",
    graph: "M5 5h4v4H5zM15 5h4v4h-4zM10 15h4v4h-4zM9 7h6M7 9v4l5 2M17 9v4l-5 2",
    check: "m5 12 4 4L19 6",
    arrow: "M5 12h14M14 7l5 5-5 5",
  };
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={paths[name]} />
    </svg>
  );
}

function relativeTime(timestamp: number) {
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - timestamp));
  if (seconds < 60) return `${seconds}s ago`;
  return `${Math.floor(seconds / 60)}m ago`;
}

function shortId(value?: string) {
  return value ? value.slice(0, 8) : "—";
}

function stageOf(snapshot: Snapshot | null) {
  if (!snapshot) return 0;
  if (snapshot.incident.status === "resolved") return 4;
  if (snapshot.episodes.some((episode) => episode.kind === "guard_rejection")) return 3;
  if (snapshot.actions.some((action) => action.status === "failed")) return 2;
  return 1;
}

function Timeline({ snapshot, selected, onSelect }: { snapshot: Snapshot; selected: string | null; onSelect: (id: string) => void }) {
  const entries = useMemo(() => {
    const episodes = snapshot.episodes.map((episode) => ({
      id: episode.id,
      time: episode.created_at,
      kind: episode.kind,
      title: episode.content,
      agent: episode.agent,
      status: episode.kind === "guard_rejection" ? "blocked" : episode.kind,
    }));
    const actions = snapshot.actions.map((action) => ({
      id: action.id,
      time: action.started_at,
      kind: "action",
      title: action.tool.replaceAll("_", " "),
      agent: action.agent,
      status: action.status,
    }));
    return [...episodes, ...actions].sort((a, b) => a.time - b.time);
  }, [snapshot]);

  return (
    <div className="timeline" role="list" aria-label="Incident memory timeline">
      {entries.map((entry, index) => (
        <button className={`timeline-entry ${selected === entry.id ? "selected" : ""}`} key={entry.id} onClick={() => onSelect(entry.id)}>
          <span className={`timeline-marker state-${entry.status}`}><span>{String(index + 1).padStart(2, "0")}</span></span>
          <span className="timeline-copy">
            <span className="timeline-meta"><strong>{entry.agent || "system"}</strong><span>{relativeTime(entry.time)}</span></span>
            <span className="timeline-title">{entry.title}</span>
            <span className="timeline-kind">{entry.kind.replaceAll("_", " ")}</span>
          </span>
        </button>
      ))}
    </div>
  );
}

function MiniGraph({ snapshot }: { snapshot: Snapshot }) {
  const services = [...new Set(snapshot.dependency_paths.flat())];
  const edges = [...new Set(snapshot.dependency_paths.flatMap(path => path.slice(1).map((target, i) => `${path[i]}|${target}`)))];
  return <div className="graph-data">
    {services.length ? <svg viewBox={`0 0 ${Math.max(660, services.length * 180)} 130`} role="img" aria-label="Service dependencies returned by FalkorDB">
      {edges.map(edge => { const [a, b] = edge.split("|"); return <g key={edge}><line className="edge" x1={services.indexOf(a) * 180 + 140} y1="55" x2={services.indexOf(b) * 180 + 20} y2="55"/><text x={(services.indexOf(a) + services.indexOf(b)) * 90 + 80} y="92">depends on →</text></g>; })}
      {services.map((name, i) => <g className="node" key={name} transform={`translate(${i * 180 + 20} 25)`}><rect width="120" height="60" rx="12"/><text x="60" y="35">{name}</text></g>)}
    </svg> : <p>No dependency paths returned by the graph.</p>}
    {snapshot.procedures.map(p => <div className="procedure-row" key={p.name}><strong>{p.name}</strong><span>APPLIES_TO → {p.target}</span><small>{p.precondition}</small></div>)}
    <details><summary>Inspect returned paths and evidence relationships</summary><pre>{JSON.stringify({dependency_paths: snapshot.dependency_paths, evidence_links: snapshot.evidence_links}, null, 2)}</pre></details>
  </div>;
}

function HypothesisStack({ hypotheses }: { hypotheses: Hypothesis[] }) {
  if (!hypotheses.length) return <Empty copy="No hypothesis has been recorded." />;
  return <div className="hypothesis-stack">{[...hypotheses].reverse().map((hypothesis) => (
    <div className={`hypothesis ${hypothesis.current ? "current" : "superseded"}`} key={hypothesis.id}>
      <div><span className="eyebrow">{hypothesis.current ? "Current belief" : "Historical / closed"}</span><span className="mono">{shortId(hypothesis.id)}</span></div>
      <p>{hypothesis.content}</p>
      <span className="validity">{hypothesis.current ? "valid now" : `closed ${relativeTime(hypothesis.valid_until ?? hypothesis.valid_from)}`}</span>
    </div>
  ))}</div>;
}

function EvidenceDetail({ snapshot, id }: { snapshot: Snapshot; id: string | null }) {
  const episode = snapshot.episodes.find((item) => item.id === id);
  const action = snapshot.actions.find((item) => item.id === id);
  const item: Episode | Action | undefined = episode ?? action;
  if (!item) return <Empty copy="Select a timeline event to inspect its stored receipt and provenance." />;
  const isEpisode = "kind" in item;
  const payload = isEpisode ? parsePayload(item.payload) : parsePayload(item.result);
  return (
    <div className="evidence-detail">
      <div className="receipt-head"><span className="receipt-stamp">FALKORDB RECEIPT</span><span className="mono">{item.id}</span></div>
      <h3>{isEpisode ? item.content : item.tool.replaceAll("_", " ")}</h3>
      <dl>
        <div><dt>Type</dt><dd>{isEpisode ? item.kind : "action"}</dd></div>
        <div><dt>Agent</dt><dd>{item.agent || "system"}</dd></div>
        <div><dt>Status</dt><dd>{isEpisode ? "persisted" : item.status}</dd></div>
        <div><dt>Freshness</dt><dd>{relativeTime(isEpisode ? item.created_at : item.started_at)}</dd></div>
      </dl>
      {Object.keys(payload).length > 0 && <pre>{JSON.stringify(payload, null, 2)}</pre>}
    </div>
  );
}

function DecisionCard({ snapshot, onSelect }: { snapshot: Snapshot; onSelect: (id: string) => void }) {
  const decision = [...snapshot.episodes].reverse().find((episode) => episode.kind === "decision");
  if (!decision) return <Empty copy="The successor has not made a remediation decision yet." />;
  const payload = parsePayload(decision.payload);
  const citations = Array.isArray(payload.evidence_ids) ? payload.evidence_ids as string[] : [];
  return (
    <div className="decision-card">
      <div className="decision-top"><span className="provider">{String(payload.provider ?? "unknown")} · {String(payload.model ?? "bounded policy")}</span><span className="validated"><Icon name="check" /> schema + references checked</span></div>
      <p className="decision-tool">{String(payload.tool ?? "handoff").replaceAll("_", " ")}</p>
      <p className="decision-reason">{decision.content}</p>
      <div className="citations"><span>Evidence cited</span>{citations.map((id) => <button className="citation" key={id} onClick={() => onSelect(id)}>EP/{shortId(id)}</button>)}</div>
    </div>
  );
}

function Empty({ copy }: { copy: string }) {
  return <div className="empty"><span className="empty-mark">◇</span><p>{copy}</p></div>;
}

function App() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [provider, setProvider] = useState<Provider>("policy");
  const [providers, setProviders] = useState({policy: true, ollama: false, gemini: false});
  const [loadTenant, setLoadTenant] = useState("");
  const [loadIncident, setLoadIncident] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backend, setBackend] = useState<"checking" | "online" | "offline">("checking");
  const stage = stageOf(snapshot);
  const occupied = snapshot?.task.status === "running" || (snapshot?.task.status === "claimed" && (snapshot.task.expires_at ?? 0) > Date.now()/1000);
  const contextPath = snapshot ? `/v1/tenants/${snapshot.tenant}/incidents/${snapshot.incident.id}` : "";

  useEffect(() => {
    request<{ status: string }>("/health").then(() => setBackend("online")).catch(() => setBackend("offline"));
    request<typeof providers>("/v1/providers").then(p => { setProviders(p); if (p.ollama) setProvider("ollama"); }).catch(() => {});
    const stored = window.localStorage.getItem("relay-active-case");
    if (!stored) return;
    try {
      const active = JSON.parse(stored) as { tenant: string; incident: string };
      setLoadTenant(active.tenant); setLoadIncident(active.incident);
      request<Snapshot>(`/v1/tenants/${active.tenant}/incidents/${active.incident}`)
        .then((restored) => {
          setSnapshot(restored);
          setSelected(restored.episodes.at(-1)?.id ?? null);
        })
        .catch(() => setError("Could not restore the saved case. Its identity is preserved; use Open case to retry."));
    } catch {
      window.localStorage.removeItem("relay-active-case");
    }
  }, []);

  useEffect(() => {
    if (!contextPath) return;
    let active = true;
    const refresh = async () => {
      try { const next = await request<Snapshot>(contextPath); if (active) { setSnapshot(next); setBackend("online"); } }
      catch { if (active) setBackend("offline"); }
    };
    const timer = window.setInterval(refresh, 2000);
    return () => { active = false; window.clearInterval(timer); };
  }, [contextPath]);

  useEffect(() => {
    if (snapshot) { setLoadTenant(snapshot.tenant); setLoadIncident(snapshot.incident.id); }
  }, [snapshot?.tenant, snapshot?.incident.id]);

  async function run(label: string, fn: () => Promise<Snapshot>) {
    setBusy(label);
    setError(null);
    try {
      const next = await fn();
      setSnapshot(next);
      window.localStorage.setItem(
        "relay-active-case",
        JSON.stringify({ tenant: next.tenant, incident: next.incident.id }),
      );
      const latest = next.episodes.at(-1);
      if (latest) setSelected(latest.id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unexpected request failure");
      if (contextPath) { try { setSnapshot(await request<Snapshot>(contextPath)); } catch { setBackend("offline"); } }
    } finally {
      setBusy(null);
    }
  }

  const base = snapshot ? `/v1/demo/${snapshot.tenant}/${snapshot.incident.id}` : "";
  const failed = snapshot?.actions.filter((action) => action.status === "failed").length ?? 0;
  const citations = snapshot?.episodes.filter((episode) => episode.kind === "decision").reduce((sum, episode) => {
    const ids = parsePayload(episode.payload).evidence_ids;
    return sum + (Array.isArray(ids) ? ids.length : 0);
  }, 0) ?? 0;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark"><Icon name="memory" /></span><div><strong>RELAY</strong><span>MEMORY OPERATIONS</span></div></div>
        <div className="topbar-center"><span className="track-label">TRACK 02</span><span>Agent memory & coordination</span></div>
        <div className="system-status"><span className={`status-light ${backend}`} /><div><strong>{backend === "online" ? "FalkorDB connected" : backend === "offline" ? "Backend offline" : "Checking core"}</strong><span>authoritative memory</span></div></div>
      </header>

      <aside className="sidebar">
        <div className="case-heading"><span className="eyebrow">Active case</span><span className="demo-chip">SYNTHETIC FIXTURE</span></div>
        <h1>{snapshot?.incident.title ?? "Inventory route failure"}</h1>
        <p className="case-id">CASE / {shortId(snapshot?.incident.id)}</p>

        <div className="stage-list">
          {[
            ["Initialize incident", "Create graph and break route"],
            ["Agent A investigates", "Controlled restart failure"],
            ["Verify guard", "Block repeated failed action"],
            ["Successor recovers", "Retrieve, decide, verify"],
          ].map(([title, note], index) => {
            const number = index + 1;
            const complete = number <= stage;
            const active = stage + 1 === number && !complete;
            return <div className={`stage ${complete ? "complete" : ""} ${active ? "active" : ""}`} key={title}><span>{complete ? "✓" : number}</span><div><strong>{title}</strong><small>{note}</small></div></div>;
          })}
        </div>

        <div className="controls">
          {!snapshot && <button className="primary" disabled={!!busy || backend !== "online"} onClick={() => run("Initializing graph", () => request("/v1/demo/start", { method: "POST", body: "{}" }))}><Icon name="bolt" />Initialize demo</button>}
          {snapshot && stage === 1 && <button className="primary" disabled={!!busy || occupied} onClick={() => run("Agent A is investigating", () => request(`${base}/first-shift`, { method: "POST" }))}>Run Agent A<Icon name="arrow" /></button>}
          {snapshot && stage === 2 && <button className="primary warning" disabled={!!busy || occupied} onClick={() => run("Testing memory guard", () => request(`${base}/guard-test`, { method: "POST" }))}><Icon name="shield" />Run guard test</button>}
          {snapshot && stage === 3 && <>
            <label className="provider-select"><span>Successor decision engine</span><select value={provider} onChange={(event) => setProvider(event.target.value as Provider)}><option value="policy">Controlled policy</option><option value="ollama" disabled={!providers.ollama}>Local Mistral{!providers.ollama ? " · unavailable" : ""}</option><option value="gemini" disabled={!providers.gemini}>Gemini API{!providers.gemini ? " · not configured" : ""}</option></select></label>
            <button className="primary success" disabled={!!busy || occupied} onClick={() => run("Successor is reasoning", () => request(`${base}/resume`, { method: "POST", body: JSON.stringify({ provider }) }))}>Launch successor<Icon name="arrow" /></button>
          </>}
          {snapshot && <button className="secondary" disabled={!!busy || occupied} onClick={() => run("Creating a fresh case", () => request("/v1/demo/start", { method: "POST", body: "{}" }))}>Start fresh case</button>}
          {snapshot?.task.status === "running" && <div className="error-banner"><strong>Operation running or delivery uncertain</strong><span>Check the original receipt. This never re-executes the tool.</span><button className="secondary" disabled={!!busy} onClick={() => run("Reconciling receipt", () => request(`${base}/reconcile`, {method: "POST"}))}>Reconcile receipt</button></div>}
          {snapshot && <button className="secondary" disabled={!!busy} onClick={() => run("Refreshing state", () => request(contextPath))}>Refresh state</button>}
          <details className="case-loader"><summary>Open an existing case</summary><label>Tenant<input aria-label="Tenant" value={loadTenant} onChange={e => setLoadTenant(e.target.value)} /></label><label>Incident ID<input aria-label="Incident ID" value={loadIncident} onChange={e => setLoadIncident(e.target.value)} /></label><button className="secondary" disabled={!!busy || !loadTenant || !loadIncident} onClick={() => run("Opening case", () => request(`/v1/tenants/${encodeURIComponent(loadTenant)}/incidents/${encodeURIComponent(loadIncident)}`))}>Open case</button></details>
          {busy && <div className="busy"><span /><p>{busy}<small>{provider === "ollama" && busy.includes("Successor") ? "Local inference may take 30–120 seconds" : "Writing verified state to the graph"}</small></p></div>}
          {error && <div className="error-banner"><strong>Stage stopped</strong><span>{error}</span></div>}
        </div>

        <div className="scope-note"><Icon name="shield" /><p><strong>Demo boundary</strong><span>Agent A is a controlled fixture. Successor uses Cognee-derived retrieval. Every stage runs in a separate worker process.</span></p></div>
      </aside>

      <main className="workspace">
        <section className="incident-strip">
          <div><span className="eyebrow">Incident state</span><strong className={`incident-state ${snapshot?.incident.status ?? "standby"}`}>{snapshot?.incident.status ?? "standby"}</strong></div>
          <div><span className="eyebrow">Task owner</span><strong>{snapshot?.task.status === "done" ? "completed" : snapshot?.task.owner || "unassigned"}</strong></div>
          <div><span className="eyebrow">Handoff generation</span><strong>{snapshot?.task.generation ?? 0}</strong></div>
          <div><span className="eyebrow">Memory freshness</span><strong>{snapshot?.episodes.at(-1) ? relativeTime(snapshot.episodes.at(-1)!.created_at) : "no episodes"}</strong></div>
          <div className="verification"><span className="eyebrow">Recovery proof</span><strong>{snapshot?.incident.status === "resolved" ? <><Icon name="check" />HTTP verified</> : "pending"}</strong></div>
        </section>

        {!snapshot ? <section className="welcome-panel">
          <div className="welcome-copy"><span className="section-index">01 / MISSION</span><h2>Memory should survive<br/><em>the agent that created it.</em></h2><p>Relay persists observations, failed fixes, changing beliefs, and task ownership in FalkorDB. A replacement agent can resume the incident without repeating the previous agent’s mistakes.</p><div className="promise-row"><span><Icon name="memory" />Persistent episodes</span><span><Icon name="shield" />Fenced ownership</span><span><Icon name="graph" />Evidence paths</span></div></div>
          <div className="welcome-diagram"><div className="agent-card first"><span>A</span><p>Investigate<br/><small>restart fails</small></p></div><div className="memory-core"><Icon name="memory" /><strong>FALKORDB</strong><span>shared incident memory</span></div><div className="agent-card second"><span>B</span><p>Resume<br/><small>recover safely</small></p></div><svg viewBox="0 0 500 100"><path d="M70 50h140M290 50h140"/><path d="m195 38 15 12-15 12M415 38l15 12-15 12"/></svg></div>
        </section> : <>
          <section className="primary-grid">
            <article className="panel timeline-panel"><PanelHead index="01" title="Incident memory" note={`${snapshot.episodes.length} persisted episodes`} /><Timeline snapshot={snapshot} selected={selected} onSelect={setSelected} /></article>
            <article className="panel decision-panel"><PanelHead index="02" title="Successor decision" note="bounded + cited" /><DecisionCard snapshot={snapshot} onSelect={setSelected} /><div className="metric-row"><div><span>Failed actions</span><strong>{failed}</strong></div><div><span>Recorded references</span><strong>{citations}</strong></div><div><span>Executed fixes</span><strong>{snapshot.actions.filter((a) => a.status === "succeeded").length}</strong></div></div></article>
            <article className="panel evidence-panel"><PanelHead index="03" title="Evidence receipt" note="select any event" /><EvidenceDetail snapshot={snapshot} id={selected} /></article>
          </section>

          <MemoryRecall snapshot={snapshot} onSelect={setSelected} />
          <section className="secondary-grid">
            <article className="panel graph-panel"><PanelHead index="04" title="Relevant graph path" note="FalkorDB query results" /><MiniGraph snapshot={snapshot} /></article>
            <article className="panel hypotheses-panel"><PanelHead index="05" title="Belief history" note="temporal validity retained" /><HypothesisStack hypotheses={snapshot.hypotheses} /></article>
          </section>
        </>}
      </main>
    </div>
  );
}

function MemoryRecall({ snapshot, onSelect }: { snapshot: Snapshot; onSelect: (id: string) => void }) {
  const latest = [...snapshot.episodes].reverse().find(e => e.kind === "memory_retrieved");
  const [query, setQuery] = useState("inventory route recovery failed restart");
  const [preview, setPreview] = useState<Dictionary | null>(null);
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { setPreview(null); setError(""); }, [snapshot.incident.id, latest?.id]);
  const manifest = preview ?? parsePayload(latest?.payload);
  const selected = Array.isArray(manifest.selected) ? manifest.selected as Dictionary[] : [];
  const workers = snapshot.episodes.filter(e => e.kind === "worker_started");
  async function search() {
    setWaiting(true); setError("");
    try { const result = await request<{manifest: Dictionary}>(`/v1/tenants/${snapshot.tenant}/incidents/${snapshot.incident.id}/recall?query=${encodeURIComponent(query)}`); setPreview(result.manifest); }
    catch (e) { setError(e instanceof Error ? e.message : "Recall failed"); }
    finally { setWaiting(false); }
  }
  return <article className="panel recall-panel">
    <PanelHead index="04" title="Memory retrieved for the successor" note="Cognee-derived · FalkorDB" />
    <div className="recall-body">
      <p>Hybrid rank fusion combines text relevance with graph evidence. Current configuration and failed attempts are pinned for safety. No embedding service is required.</p>
      <div className="recall-search"><input aria-label="Memory search" maxLength={500} value={query} onChange={e => setQuery(e.target.value)} /><button className="secondary" disabled={waiting || !query.trim()} onClick={search}>{waiting ? "Retrieving…" : "Search memory"}</button>{preview && <button className="secondary" onClick={() => setPreview(null)}>Show actual agent retrieval</button>}</div>
      {error && <p role="alert">{error}</p>}
      <div className="worker-proof">{workers.map(e => { const p = parsePayload(e.payload); return <button key={e.id} className="citation" onClick={() => onSelect(e.id)}>{e.agent} · PID {String(p.pid)} · run {shortId(String(p.run_id))}</button>; })}</div>
      <p className="recall-label">{preview ? "Search preview — not used by a decision" : latest ? "Persisted context actually supplied to the successor" : "The successor has not retrieved memory yet"}{selected.length > 0 && ` · ${selected.length} episodes · ${manifest.context_bytes} bytes`}</p>
      <div className="recall-results">{selected.map(e => <button key={String(e.id)} onClick={() => onSelect(String(e.id))}><strong>{String(e.kind).replaceAll("_", " ")}</strong><span>{String(e.content)}</span><small>{String(e.reason)} · {e.score ? Number(e.score).toFixed(4) : "pinned"}</small></button>)}</div>
      {selected.length > 0 && <details><summary>Retrieval manifest, graph triplets and context hash</summary><pre>{JSON.stringify(manifest, null, 2)}</pre></details>}
    </div>
  </article>;
}

function PanelHead({ index, title, note }: { index: string; title: string; note: string }) {
  return <div className="panel-head"><div><span>{index}</span><h2>{title}</h2></div><p>{note}</p></div>;
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
