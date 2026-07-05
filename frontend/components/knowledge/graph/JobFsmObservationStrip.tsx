import {
  formatAggregateStatus,
  jobFsmSubsetForAggregate,
  VOCABULARY_DOMAIN_LABELS,
} from "@/lib/jobFsmVocabulary";
import { cn } from "@/lib/cn";
import type { JobFsmObservation } from "@/lib/knowledgeTypes";

export type JobFsmObservationStripProps = {
  observation: JobFsmObservation;
  className?: string;
};

/**
 * Read-only MB2 Job FSM observation (SoR §5) — distinct from product lifecycle badges.
 */
export function JobFsmObservationStrip({
  observation,
  className,
}: JobFsmObservationStripProps) {
  const runningJobs = observation.projection_jobs.filter(
    (job) => job.aggregate_status === "running"
  );
  const recentJobs = observation.projection_jobs.slice(0, 6);

  return (
    <section
      className={cn("rounded-md border border-border bg-surface-muted p-4", className)}
      data-testid="job-fsm-observation"
      aria-label="MB2 Job FSM observation"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold text-ink">Job FSM (projection)</h2>
          <p className="mt-1 text-xs text-ink-muted">
            SoR §5 aggregate status — read-only consumer (INV-R-11). Not product lifecycle.
          </p>
        </div>
        <span className="rounded-full border border-border bg-surface px-2 py-0.5 text-xs text-ink-subtle">
          {observation.read_only ? "Read-only" : "Live"}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap gap-2" data-testid="vocabulary-domains">
        {observation.vocabulary_domains.map((domain) => (
          <span
            key={domain.domain}
            className="rounded-md border border-dashed border-border px-2 py-1 text-xs text-ink-subtle"
            title={domain.notes}
          >
            {VOCABULARY_DOMAIN_LABELS[
              domain.domain as keyof typeof VOCABULARY_DOMAIN_LABELS
            ] ?? domain.vocabulary}
          </span>
        ))}
      </div>

      {runningJobs.length > 0 && (
        <p className="mt-3 text-xs text-accent" data-testid="job-fsm-running">
          {runningJobs.length} job in esecuzione
        </p>
      )}

      <ul className="mt-3 space-y-1" data-testid="job-fsm-projection-list">
        {recentJobs.map((job) => (
          <li
            key={job.ewo_id}
            className="flex flex-wrap items-center gap-2 font-mono text-xs text-ink-muted"
          >
            <span>{job.ewo_id}</span>
            <span className="rounded bg-surface px-1.5 py-0.5 text-ink">
              {formatAggregateStatus(job.aggregate_status)}
            </span>
            <span className="text-ink-subtle">
              → {job.job_fsm_subset ?? jobFsmSubsetForAggregate(job.aggregate_status)}
            </span>
          </li>
        ))}
      </ul>

      <p className="mt-3 text-xs text-ink-subtle">{observation.inv_r_11_note}</p>
    </section>
  );
}
