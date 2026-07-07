import Link from "next/link";

/**
 * PX-3.10 guided research placeholder — full trail deferred to PX-3 scope.
 * Layer: Business (Product Plane)
 */
export function ResearchGuidedStub() {
  return (
    <div className="mx-auto max-w-content space-y-6">
      <header>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">PX-3.10</p>
        <h1 className="mt-1 text-2xl font-semibold text-ink">Esplorazione guidata</h1>
        <p className="mt-2 max-w-prose text-sm leading-relaxed text-ink-muted">
          Trail lineare con basket — implementazione completa in arrivo.
        </p>
      </header>

      <div className="rounded-lg border border-dashed border-border bg-surface-muted p-8 text-center">
        <p className="text-sm text-ink-muted">
          Nel frattempo esplora la{" "}
          <Link href="/research/canvas" className="font-medium text-accent hover:underline cursor-pointer">
            mappa concettuale
          </Link>{" "}
          o il grafo{" "}
          <Link href="/knowledge/graph" className="font-medium text-accent hover:underline cursor-pointer">
            Knowledge
          </Link>
          .
        </p>
        <Link
          href="/research"
          className="mt-4 inline-block text-sm font-medium text-accent hover:underline cursor-pointer"
        >
          ← Torna all&apos;hub Research
        </Link>
      </div>
    </div>
  );
}
