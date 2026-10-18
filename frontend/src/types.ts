export type Dictionary = Record<string, unknown>;

export interface Incident {
  id: string;
  title: string;
  status: "open" | "resolved";
  created_at: number;
  resolved_at?: number;
}

export interface Task {
  id: string;
  status: "open" | "claimed" | "running" | "done";
  generation: number;
  owner?: string;
  expires_at?: number;
}

export interface Episode {
  id: string;
  kind: string;
  agent: string;
  content: string;
  created_at: number;
  payload?: string;
}

export interface Hypothesis {
  id: string;
  content: string;
  current: boolean;
  valid_from: number;
  valid_until?: number;
}

export interface Action {
  id: string;
  tool: string;
  status: "running" | "failed" | "succeeded";
  agent: string;
  started_at: number;
  finished_at?: number;
  result?: string;
}

export interface Procedure {
  name: string;
  precondition: string;
  target: string;
}

export interface EvidenceLink {
  source: string;
  relation: "SUPPORTS" | "CONTRADICTS";
  target: string;
}

export interface Snapshot {
  tenant: string;
  incident: Incident;
  task: Task;
  episodes: Episode[];
  hypotheses: Hypothesis[];
  actions: Action[];
  failed_actions: Action[];
  dependency_paths: string[][];
  procedures: Procedure[];
  evidence_links: EvidenceLink[];
}

export type Provider = "policy" | "ollama" | "gemini";
