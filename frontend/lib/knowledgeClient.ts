import type {
  ConceptDefinitionEnvelope,
  ConceptDetailEnvelope,
  ConceptHeaderEnvelope,
  ConformanceProjection,
  JobFsmObservation,
  KnowledgeGraphResponse,
  KnowledgeObjectEnvelope,
  KnowledgeObjectListResponse,
  KnowledgeObjectType,
  ProgramGraphObservation,
} from "@/lib/knowledgeTypes";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEFAULT_PROJECT = "thesis-agent";

export async function listKnowledgeObjects(
  options: {
    projectId?: string;
    type?: KnowledgeObjectType;
    includeDeprecated?: boolean;
  } = {}
): Promise<KnowledgeObjectListResponse> {
  const projectId = options.projectId ?? DEFAULT_PROJECT;
  const params = new URLSearchParams();
  if (options.type != null) params.set("type", options.type);
  if (options.includeDeprecated) params.set("include_deprecated", "true");

  const qs = params.toString();
  const url = `${BASE}/projects/${projectId}/knowledge/objects${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Knowledge list failed: ${res.status}`);
  }
  return res.json() as Promise<KnowledgeObjectListResponse>;
}

export async function getKnowledgeObject(
  slug: string,
  projectId: string = DEFAULT_PROJECT
): Promise<KnowledgeObjectEnvelope> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/knowledge/objects/${encodeURIComponent(slug)}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Knowledge object not found: ${slug}`);
  }
  return res.json() as Promise<KnowledgeObjectEnvelope>;
}

export async function getConceptHeader(
  slug: string,
  projectId: string = DEFAULT_PROJECT
): Promise<ConceptHeaderEnvelope> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}/header`,
    { cache: "no-store" }
  );
  if (res.status === 404) {
    throw new Error("concept_not_found");
  }
  if (!res.ok) {
    throw new Error(`Concept header failed: ${res.status}`);
  }
  return res.json() as Promise<ConceptHeaderEnvelope>;
}

export async function getConceptDefinition(
  slug: string,
  projectId: string = DEFAULT_PROJECT
): Promise<ConceptDefinitionEnvelope> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}/definition`,
    { cache: "no-store" }
  );
  if (res.status === 404) {
    throw new Error("concept_not_found");
  }
  if (!res.ok) {
    throw new Error(`Concept definition failed: ${res.status}`);
  }
  return res.json() as Promise<ConceptDefinitionEnvelope>;
}

export async function getConceptDetail(
  slug: string,
  projectId: string = DEFAULT_PROJECT
): Promise<ConceptDetailEnvelope> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}`,
    { cache: "no-store" }
  );
  if (res.status === 404) {
    throw new Error("concept_not_found");
  }
  if (!res.ok) {
    throw new Error(`Concept detail failed: ${res.status}`);
  }
  return res.json() as Promise<ConceptDetailEnvelope>;
}

export async function getConformanceProjection(
  projectId: string = DEFAULT_PROJECT
): Promise<ConformanceProjection> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/conformance/projection`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Projection fetch failed: ${res.status}`);
  }
  return res.json() as Promise<ConformanceProjection>;
}

export async function getProgramGraphObservation(
  projectId: string = DEFAULT_PROJECT
): Promise<ProgramGraphObservation> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/conformance/program-graph`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Program graph fetch failed: ${res.status}`);
  }
  return res.json() as Promise<ProgramGraphObservation>;
}

export async function getKnowledgeGraph(
  options: {
    projectId?: string;
    focus?: string;
    depth?: number;
    maxNodes?: number;
    view?: "graph" | "list";
  } = {}
): Promise<KnowledgeGraphResponse> {
  const projectId = options.projectId ?? DEFAULT_PROJECT;
  const params = new URLSearchParams();
  if (options.focus != null) params.set("focus", options.focus);
  if (options.depth != null) params.set("depth", String(options.depth));
  if (options.maxNodes != null) params.set("max_nodes", String(options.maxNodes));
  if (options.view != null) params.set("view", options.view);

  const qs = params.toString();
  const url = `${BASE}/projects/${projectId}/knowledge/graph${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Knowledge graph fetch failed: ${res.status}`);
  }
  return res.json() as Promise<KnowledgeGraphResponse>;
}

export async function getJobFsmObservation(
  projectId: string = DEFAULT_PROJECT
): Promise<JobFsmObservation> {
  const res = await fetch(
    `${BASE}/projects/${projectId}/conformance/job-fsm`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Job FSM observation fetch failed: ${res.status}`);
  }
  return res.json() as Promise<JobFsmObservation>;
}
