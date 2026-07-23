"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProgressRing } from "@/components/ProgressRing";
import { EntityCard } from "@/components/EntityCard";
import { ApiDegradedBanner } from "@/components/ui/ApiDegradedBanner";
import type { ActivityItem } from "@/lib/homeTypes";
import { mergeContinuaTarget } from "@/lib/continuaLink";
import type { ContinueTarget } from "@/lib/progress";
import { progressPhaseLabel } from "@/lib/progress";
import { getPendingProposalCount } from "@/lib/sessionState";
import { cn } from "@/lib/cn";

const QUICK_ACTIONS = [
  { href: "/research", label: "Ricerca", description: "Esplora il panorama concettuale" },
  { href: "/writing", label: "Scrittura", description: "Apri l'editor dei capitoli" },
  { href: "/review", label: "Revisione", description: "Revisiona con l'assistente" },
  { href: "/sources/upload", label: "Importa documento", description: "Aggiungi una nuova fonte" },
] as const;

/** PX-2 activity feed card kinds — UI spec §7 */
export type ActivityFeedKind =
  | "chapter"
  | "proposal_update"
  | "binding_decision"
  | "source_candidate"
  | "session_bundle";

export type HomeActivityItem = {
  kind: ActivityFeedKind;
  title: string;
  subtitle?: string;
  meta?: string;
  href?: string;
};

export type HomeViewProps = {
  progressPct: number;
  continueTarget: ContinueTarget;
  activity?: ActivityItem[];
  /** PX-2 activity feed with proposal types */
  activityFeed?: HomeActivityItem[];
  /** Error Contract v1 — API load failed; do not treat as zero progress */
  chaptersLoadError?: string | null;
  /** When false, empty progress uses neutral copy (no fashion thesis phase). */
  fashionEmptyPhase?: boolean;
};

const ACTIVITY_LABELS: Record<ActivityFeedKind, string> = {
  chapter: "Capitolo",
  proposal_update: "Aggiornamento proposto",
  binding_decision: "Decisione vincolante",
  source_candidate: "Nuova fonte",
  session_bundle: "Chiudi sessione",
};

function ActivityIcon({
  kind,
  className,
}: {
  kind: ActivityFeedKind;
  className?: string;
}) {
  const props = {
    className: cn("h-5 w-5 shrink-0", className),
    "aria-hidden": true as const,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
  };

  switch (kind) {
    case "binding_decision":
      return (
        <svg {...props}>
          <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
      );
    case "source_candidate":
      return (
        <svg {...props}>
          <path d="M12 6v12m-3-3h6M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      );
    case "session_bundle":
      return (
        <svg {...props}>
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
        </svg>
      );
    case "proposal_update":
      return (
        <svg {...props}>
          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
          <path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      );
    default:
      return null;
  }
}

function ActivityFeedCard({ item }: { item: HomeActivityItem }) {
  const accentClass =
    item.kind === "binding_decision" ? "text-warning" : "text-accent";

  const body = (
    <div className="flex gap-3">
      {item.kind !== "chapter" && (
        <ActivityIcon kind={item.kind} className={cn("mt-0.5", accentClass)} />
      )}
      <div className="min-w-0 flex-1">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          {ACTIVITY_LABELS[item.kind]}
        </span>
        <span className="mt-1 block text-sm font-semibold text-ink">{item.title}</span>
        {item.subtitle != null && (
          <span className="mt-0.5 block text-sm text-ink-muted">{item.subtitle}</span>
        )}
        {item.meta != null && (
          <span className="mt-2 block text-xs text-ink-subtle">{item.meta}</span>
        )}
      </div>
    </div>
  );

  const classes = cn(
    "block rounded-md border border-border bg-surface p-4 shadow-sm transition-colors",
    item.href != null && "hover:border-border-strong hover:bg-surface-muted"
  );

  if (item.href != null) {
    return (
      <Link href={item.href} className={classes}>
        {body}
      </Link>
    );
  }

  return <article className={classes}>{body}</article>;
}

/**
 * Home module — Spec §5.1, design-system/thesisos/pages/home.md
 * Layer: Business (Product Plane)
 */
export function HomeView({
  progressPct,
  continueTarget,
  activity = [],
  activityFeed,
  chaptersLoadError = null,
  fashionEmptyPhase = false,
}: HomeViewProps) {
  const phase = progressPhaseLabel(progressPct, { fashionEmptyPhase });
  const [continua, setContinua] = useState(continueTarget);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    setContinua(mergeContinuaTarget(continueTarget));
    setPendingCount(getPendingProposalCount());

    const onBundle = () => setPendingCount(getPendingProposalCount());
    window.addEventListener("thesisos:proposal-bundle-resolved", onBundle);
    return () =>
      window.removeEventListener("thesisos:proposal-bundle-resolved", onBundle);
  }, [continueTarget]);

  const feedItems = activityFeed ?? [];
  const legacyItems = activityFeed == null ? activity : [];
  const hasActivity = feedItems.length > 0 || legacyItems.length > 0;

  return (
    <div className="mx-auto max-w-content">
      <header className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">
            Home
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Riprendi da dove hai lasciato — la tesi avanza un passo alla volta.
          </p>
        </div>
        {pendingCount > 0 && (
          <span
            className="inline-flex shrink-0 items-center rounded-full bg-accent px-2.5 py-0.5 text-xs font-medium text-ink-inverse"
            data-testid="home-pending-badge"
            aria-label={`${pendingCount} proposte in sospeso`}
          >
            {pendingCount}
          </span>
        )}
      </header>

      {chaptersLoadError ? (
        <ApiDegradedBanner
          message={chaptersLoadError}
          className="mb-6"
          testId="home-chapters-load-degraded"
        />
      ) : null}

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
          href={continua.href}
          className={cn(
            "inline-flex shrink-0 items-center justify-center gap-2 rounded-md",
            "bg-accent px-5 py-2.5 text-sm font-medium text-ink-inverse",
            "transition-colors duration-200 hover:bg-accent-muted",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "focus-visible:outline-accent cursor-pointer"
          )}
          data-testid="continua-link"
        >
          Continua
          <span aria-hidden="true">→</span>
          <span className="sr-only">: {continua.label}</span>
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
                data-testid={
                  action.href === "/sources/upload" ? "home-import-cta" : undefined
                }
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
        {hasActivity ? (
          <ul className="space-y-3">
            {feedItems.map((item, i) => (
              <li key={`feed-${item.kind}-${item.title}-${i}`}>
                <ActivityFeedCard item={item} />
              </li>
            ))}
            {legacyItems.map((item, i) => (
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
                href="/sources/upload"
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

/** Sidebar nav badge count — wire in AppShell (Integration B). */
export function getHomeNavProposalBadgeCount(): number {
  return getPendingProposalCount();
}
