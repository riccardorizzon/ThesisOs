import Link from "next/link";
import { ProgressRing } from "@/components/ProgressRing";
import { EntityCard } from "@/components/EntityCard";
import type { ActivityItem } from "@/lib/homeStub";
import type { ContinueTarget } from "@/lib/progress";
import { progressPhaseLabel } from "@/lib/progress";
import { cn } from "@/lib/cn";

const QUICK_ACTIONS = [
  { href: "/research", label: "Ricerca", description: "Esplora il panorama concettuale" },
  { href: "/writing", label: "Scrittura", description: "Apri l'editor dei capitoli" },
  { href: "/review", label: "Revisione", description: "Revisiona con l'assistente" },
  { href: "/documents/upload", label: "Importa documento", description: "Aggiungi una nuova fonte" },
] as const;

export type HomeViewProps = {
  progressPct: number;
  continueTarget: ContinueTarget;
  activity: ActivityItem[];
};

/**
 * Home module — Spec §5.1, design-system/thesisos/pages/home.md
 * Layer: Business (Product Plane)
 */
export function HomeView({
  progressPct,
  continueTarget,
  activity,
}: HomeViewProps) {
  const phase = progressPhaseLabel(progressPct);

  return (
    <div className="mx-auto max-w-content">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Home
        </h1>
        <p className="mt-1 text-sm text-ink-muted">
          Riprendi da dove hai lasciato — la tesi avanza un passo alla volta.
        </p>
      </header>

      <section
        aria-labelledby="home-progress-heading"
        className="mb-10 flex flex-col gap-8 rounded-lg border border-border bg-surface p-6 shadow-sm md:flex-row md:items-center md:justify-between"
      >
        <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center">
          <ProgressRing
            value={progressPct}
            label="Avanzamento tesi"
            sublabel={phase}
          />
          <div className="max-w-sm">
            <h2
              id="home-progress-heading"
              className="text-lg font-medium text-ink"
            >
              {phase}
            </h2>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">
              Progresso calcolato dallo stato dei capitoli — non una stima del
              modello.
            </p>
          </div>
        </div>
        <Link
          href={continueTarget.href}
          className={cn(
            "inline-flex shrink-0 items-center justify-center gap-2 rounded-md",
            "bg-accent px-5 py-2.5 text-sm font-medium text-white",
            "transition-colors duration-200 hover:bg-accent-muted",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "focus-visible:outline-accent cursor-pointer"
          )}
        >
          Continua
          <span aria-hidden="true">→</span>
          <span className="sr-only">: {continueTarget.label}</span>
        </Link>
      </section>

      <section aria-labelledby="home-actions-heading" className="mb-10">
        <h2
          id="home-actions-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Azioni rapide
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_ACTIONS.map((action) => (
            <li key={action.href}>
              <Link
                href={action.href}
                className={cn(
                  "flex h-full flex-col rounded-md border border-border bg-surface p-4 shadow-sm",
                  "transition-colors duration-200 hover:border-border-strong hover:bg-surface-muted",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent cursor-pointer"
                )}
              >
                <span className="text-sm font-semibold text-ink">
                  {action.label}
                </span>
                <span className="mt-1 text-xs leading-relaxed text-ink-muted">
                  {action.description}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="home-activity-heading">
        <h2
          id="home-activity-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Attività recente
        </h2>
        {activity.length > 0 ? (
          <ul className="space-y-3">
            {activity.map((item, i) => (
              <li key={`${item.entityType}-${item.title}-${i}`}>
                <EntityCard
                  entityType={item.entityType}
                  title={item.title}
                  subtitle={item.subtitle}
                  meta={item.meta}
                  href={item.href}
                />
              </li>
            ))}
          </ul>
        ) : (
          <div className="rounded-md border border-dashed border-border bg-surface-muted p-8 text-center">
            <p className="text-sm text-ink-muted">
              Nessuna attività recente. Inizia con{" "}
              <Link
                href="/writing"
                className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
              >
                Scrittura
              </Link>{" "}
              o{" "}
              <Link
                href="/documents/upload"
                className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
              >
                importa un documento
              </Link>
              .
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
