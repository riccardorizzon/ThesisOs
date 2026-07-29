/** Human-readable beta limitations — demo handout copy in product UI. */
export const BETA_LIMITATIONS = [
  "Single-user — nessun multi-tenant; adatto a demo e uso personale.",
  "Corpus-bound — le risposte AI usano solo documenti indicizzati; niente ricerca web live.",
  "Tunnel pubblico fragile — l'URL Cloudflare può cambiare; per demo stabile usare localhost.",
  "Originali file — molti PDF storici non sono su disco; RAG funziona da chunk Postgres.",
] as const;

export function BetaLimitationsPanel() {
  return (
    <div
      className="space-y-3 rounded-lg border border-border bg-surface p-4"
      data-testid="beta-limitations-panel"
    >
      <div>
        <h2 className="text-sm font-semibold text-ink">Beta — limitazioni note</h2>
        <p className="mt-1 text-xs text-ink-muted">
          Versione <span className="font-mono">v2.0.0-rc.2</span>. Dettaglio tecnico in{" "}
          <code className="rounded bg-surface-muted px-1">docs/KNOWN_LIMITATIONS.md</code>.
        </p>
      </div>
      <ul className="list-disc space-y-1.5 pl-5 text-sm text-ink-muted">
        {BETA_LIMITATIONS.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
