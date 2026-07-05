/**
 * Job FSM vocabulary helpers — PX3-EWO-009 (SoR §5 vs product §4).
 */

export type AggregateStatus =
  | "waiting"
  | "ready"
  | "running"
  | "pass"
  | "fail"
  | "locked";

export const AGGREGATE_LABELS: Record<AggregateStatus, string> = {
  waiting: "In attesa",
  ready: "Pronto",
  running: "In esecuzione",
  pass: "Completato",
  fail: "Fallito",
  locked: "Bloccato",
};

export const AGGREGATE_TO_JOB_FSM: Record<AggregateStatus, string> = {
  waiting: "CREATED",
  ready: "READY",
  running: "RUNNING",
  pass: "DONE",
  fail: "FAILED",
  locked: "LOCKED",
};

export const VOCABULARY_DOMAIN_LABELS = {
  product_lifecycle: "Product lifecycle (PX-3 §4)",
  mb2_aggregate: "MB2 aggregate (SoR §5.3)",
  mb2_job_fsm: "Job FSM subset (SoR §5.1)",
} as const;

export function formatAggregateStatus(status: string): string {
  if (status in AGGREGATE_LABELS) {
    return AGGREGATE_LABELS[status as AggregateStatus];
  }
  return status;
}

export function jobFsmSubsetForAggregate(status: string): string {
  if (status in AGGREGATE_TO_JOB_FSM) {
    return AGGREGATE_TO_JOB_FSM[status as AggregateStatus];
  }
  return "CREATED";
}
