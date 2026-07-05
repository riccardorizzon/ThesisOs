import { cn } from "@/lib/cn";
import type { ProgramGraphObservation, ProgramGraphWave } from "@/lib/knowledgeTypes";

export type ProgramTracePanelProps = {
  graph: ProgramGraphObservation;
  className?: string;
};

function WaveCard({ wave }: { wave: ProgramGraphWave }) {
  return (
    <article
      className="rounded-lg border border-border bg-surface p-4 shadow-sm"
      data-testid={`wave-${wave.wave_id}`}
    >
      <header className="flex flex-wrap items-baseline gap-2">
        <h3 className="text-sm font-semibold text-ink">{wave.title}</h3>
        <span className="font-mono text-xs text-ink-muted">{wave.wave_id}</span>
        {wave.status != null && (
          <span className="rounded-full bg-accent-subtle px-2 py-0.5 text-xs text-accent">
            {wave.status}
          </span>
        )}
      </header>

      <dl className="mt-3 grid gap-1 text-xs text-ink-muted">
        {wave.depends_on_wave != null && (
          <div className="flex gap-2">
            <dt className="font-medium">depends_on_wave</dt>
            <dd className="font-mono">{wave.depends_on_wave}</dd>
          </div>
        )}
        {wave.unblocks != null && (
          <div className="flex gap-2">
            <dt className="font-medium">unblocks</dt>
            <dd className="font-mono">{wave.unblocks}</dd>
          </div>
        )}
        {wave.execute_in_parallel && (
          <div>
            <dt className="sr-only">parallel</dt>
            <dd>execute_in_parallel</dd>
          </div>
        )}
        {wave.merge_order.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <dt className="font-medium">merge_order</dt>
            <dd className="font-mono">{wave.merge_order.join(" → ")}</dd>
          </div>
        )}
      </dl>

      <ul className="mt-3 flex flex-wrap gap-2" data-testid={`wave-nodes-${wave.wave_id}`}>
        {wave.nodes.map((node) => (
          <li
            key={node.node_id}
            className={cn(
              "rounded-md border px-2 py-1 font-mono text-xs",
              node.node_type === "integration"
                ? "border-amber-200 bg-amber-50 text-amber-900"
                : "border-border bg-muted text-ink"
            )}
            data-testid={`node-${node.node_id}`}
          >
            {node.node_id}
          </li>
        ))}
      </ul>
    </article>
  );
}

/** Program Trace panel — wave DAG (PX3-EWO-008, read-only; no ReadySet). */
export function ProgramTracePanel({ graph, className }: ProgramTracePanelProps) {
  const waveDepends = graph.edges.filter((e) => e.edge_type === "depends_on_wave");

  return (
    <section
      className={cn("space-y-6", className)}
      data-testid="program-trace-panel"
    >
      <header className="space-y-1">
        <p className="text-xs uppercase tracking-wide text-ink-muted">
          Program Trace · read-only
        </p>
        <h2 className="text-xl font-semibold text-ink">{graph.program_id}</h2>
        <p className="text-sm text-ink-muted">
          Source: <span className="font-mono">{graph.source}</span> · parent:{" "}
          <span className="font-mono">{graph.parent_program}</span>
        </p>
        <p
          className="text-xs text-ink-muted"
          data-testid="inv-r-12-boundary"
        >
          INV-R-12: structure observation only — no ReadySet or CriticalPath
          computation.
        </p>
      </header>

      {waveDepends.length > 0 && (
        <div className="rounded-lg border border-dashed border-border p-4">
          <h3 className="text-sm font-medium text-ink">Wave dependencies</h3>
          <ul className="mt-2 space-y-1 font-mono text-xs text-ink-muted">
            {waveDepends.map((edge) => (
              <li key={`${edge.source}-${edge.target}`} data-testid="wave-edge">
                {edge.source} → {edge.target}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {graph.waves.map((wave) => (
          <WaveCard key={wave.wave_id} wave={wave} />
        ))}
      </div>
    </section>
  );
}
