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
import { apiBaseUrl } from "@/lib/apiBase";
import { activeProjectScope } from "@/lib/projectScope";

export async function listKnowledgeObjects(
  options: {
    projectId?: string;
    type?: KnowledgeObjectType;
    includeDeprecated?: boolean;
  } = {}
): Promise<KnowledgeObjectListResponse> {
  const projectId = activeProjectScope(options.projectId);
  const params = new URLSearchParams();
  if (options.type != null) params.set("type", options.type);
  if (options.includeDeprecated) params.set("include_deprecated", "true");

  const qs = params.toString();
  const url = `${apiBaseUrl()}/projects/${projectId}/knowledge/objects${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Knowledge list failed: ${res.status}`);
  }
  return res.json() as Promise<KnowledgeObjectListResponse>;
}

export async function getKnowledgeObject(
  slug: string,
  projectId: string = activeProjectScope()
): Promise<KnowledgeObjectEnvelope> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/knowledge/objects/${encodeURIComponent(slug)}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Knowledge object not found: ${slug}`);
  }
  return res.json() as Promise<KnowledgeObjectEnvelope>;
}

export async function getConceptHeader(
  slug: string,
  projectId: string = activeProjectScope()
): Promise<ConceptHeaderEnvelope> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}/header`,
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
  projectId: string = activeProjectScope()
): Promise<ConceptDefinitionEnvelope> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}/definition`,
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
  projectId: string = activeProjectScope()
): Promise<ConceptDetailEnvelope> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/knowledge/concepts/${encodeURIComponent(slug)}`,
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

export async function searchKnowledge(
  query: string,
  options: { projectId?: string; limit?: number } = {}
): Promise<{ query: string; results: KnowledgeObjectEnvelope[]; total: number }> {
  const projectId = activeProjectScope(options.projectId);
  const params = new URLSearchParams({ q: query });
  if (options.limit != null) params.set("limit", String(options.limit));
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/knowledge/search?${params}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Knowledge search failed: ${res.status}`);
  }
  return res.json() as Promise<{
    query: string;
    results: KnowledgeObjectEnvelope[];
    total: number;
  }>;
}

export async function getConformanceProjection(
  projectId: string = activeProjectScope()
): Promise<ConformanceProjection> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/conformance/projection`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Projection fetch failed: ${res.status}`);
  }
  return res.json() as Promise<ConformanceProjection>;
}

export async function getProgramGraphObservation(
  projectId: string = activeProjectScope()
): Promise<ProgramGraphObservation> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/conformance/program-graph`,
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
    profile?: "canvas" | "navigation";
  } = {}
): Promise<KnowledgeGraphResponse> {
  const projectId = activeProjectScope(options.projectId);
  const params = new URLSearchParams();
  if (options.focus != null) params.set("focus", options.focus);
  if (options.depth != null) params.set("depth", String(options.depth));
  if (options.maxNodes != null) params.set("max_nodes", String(options.maxNodes));
  if (options.view != null) params.set("view", options.view);
  if (options.profile === "canvas") params.set("profile", "canvas");

  const qs = params.toString();
  const url = `${apiBaseUrl()}/projects/${projectId}/knowledge/graph${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Knowledge graph fetch failed: ${res.status}`);
  }
  return res.json() as Promise<KnowledgeGraphResponse>;
}

export async function getJobFsmObservation(
  projectId: string = activeProjectScope()
): Promise<JobFsmObservation> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${projectId}/conformance/job-fsm`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    throw new Error(`Job FSM observation fetch failed: ${res.status}`);
  }
  return res.json() as Promise<JobFsmObservation>;
}
