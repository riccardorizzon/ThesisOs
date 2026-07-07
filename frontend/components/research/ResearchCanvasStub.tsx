import Link from "next/link";

export type ResearchCanvasStubProps = {
  focus?: string;
  view?: string;
};

/**
 * PX-5 canvas route scaffold — viewport implementation deferred to PX5-EWO-003+.
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasStub({ focus, view }: ResearchCanvasStubProps) {
  return (
    <div className="mx-auto max-w-content space-y-6">
      <header>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">PX-5</p>
        <h1 className="mt-1 text-2xl font-semibold text-ink">Mappa concettuale</h1>
        <p className="mt-2 max-w-prose text-sm leading-relaxed text-ink-muted">
          Canvas spaziale — implementazione viewport in arrivo (Wave C).
        </p>
      </header>

      <div className="rounded-lg border border-dashed border-border bg-surface-muted p-8 text-center">
        <p className="text-sm text-ink-muted">
          {focus != null
            ? `Focus concetto: ${focus}`
            : view != null
              ? `Vista salvata: ${view}`
              : "Viewport canvas non ancora implementato."}
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
