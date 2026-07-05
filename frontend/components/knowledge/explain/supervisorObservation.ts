import type { ConformanceProjection } from "@/lib/knowledgeTypes";

/**
 * Observable §10 / INV-R-16 — product must not autonomously progress past a
 * Supervisor WAIT until delegation for the current wave scope is observable.
 * Does not implement Runtime Supervisor logic.
 */
export function supervisorAllowsDefinitionProgression(
  projection: ConformanceProjection | null
): boolean {
  if (projection == null) return true;
  if (projection.supervisor.state !== "WAIT") return true;

  const wave = projection.waves?.wave_b_supervisor;
  const job = wave?.jobs?.["PX3-EWO-006"];
  return job?.status === "ready" || job?.status === "running" || job?.status === "pass";
}

export function supervisorObservationLabel(
  projection: ConformanceProjection | null
): string | null {
  if (projection == null) return null;
  if (projection.supervisor.state !== "WAIT") return null;
  if (supervisorAllowsDefinitionProgression(projection)) return null;
  const reason = projection.supervisor.reason;
  if (reason != null && reason !== "") {
    return `Supervisor WAIT — ${reason} (§10)`;
  }
  return "Supervisor WAIT — progressione sospesa (§10)";
}
