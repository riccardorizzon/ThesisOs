import Link from "next/link";
import { cn } from "@/lib/cn";
import { ResearchResumeSection } from "@/components/research/ResearchResumeSection";

export type ResearchHubPageProps = {
  conceptCount: number;
};

type ModeCardProps = {
  title: string;
  description: string;
  href: string;
  cta: string;
  icon: "map" | "route";
  isDisabled?: boolean;
};

function ModeIcon({ kind, className }: { kind: ModeCardProps["icon"]; className?: string }) {
  const props = {
    className: cn("h-6 w-6 shrink-0", className),
    "aria-hidden": true as const,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
  };

  if (kind === "route") {
    return (
      <svg {...props}>
        <path d="M4 6h16M4 12h10M4 18h6" strokeLinecap="round" />
        <circle cx="18" cy="12" r="2" />
        <circle cx="20" cy="18" r="2" />
      </svg>
    );
  }

  return (
    <svg {...props}>
      <path d="M3 7l6-3 6 3 6-3v13l-6 3-6-3-6 3V7z" />
      <path d="M9 4v13M15 7v13" />
    </svg>
  );
}

function ModeCard({ title, description, href, cta, icon, isDisabled = false }: ModeCardProps) {
  const body = (
    <div
      data-testid={isDisabled ? "mode-card-disabled" : "mode-card-enabled"}
      className={cn(
        "flex h-full flex-col rounded-lg border bg-surface p-5 transition-colors",
        isDisabled
          ? "cursor-not-allowed border-border opacity-60"
          : "border-border hover:border-accent/40 hover:bg-surface-muted cursor-pointer"
      )}
    >
      <div className="mb-3 flex items-center gap-3 text-accent">
        <ModeIcon kind={icon} />
        <h2 className="text-base font-semibold text-ink">{title}</h2>
      </div>
      <p className="mb-4 flex-1 text-sm leading-relaxed text-ink-muted">{description}</p>
      <span
        className={cn(
          "text-sm font-medium",
          isDisabled ? "text-ink-subtle" : "text-accent"
        )}
      >
        {cta}
      </span>
    </div>
  );

  if (isDisabled) {
    return body;
  }

  return (
    <Link href={href} className="block h-full cursor-pointer">
      {body}
    </Link>
  );
}

/**
 * PX-5 Research hub — mode selection entry point.
 * Layer: Business (Product Plane)
 */
export function ResearchHubPage({ conceptCount }: ResearchHubPageProps) {
  const hasConcepts = conceptCount > 0;

  return (
    <div className="mx-auto max-w-content space-y-8">
      <header>
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">PX-5</p>
        <h1 className="mt-1 text-2xl font-semibold text-ink">Research</h1>
        <p className="mt-2 max-w-prose text-sm leading-relaxed text-ink-muted">
          Esplora il panorama concettuale — mappa spaziale o trail guidato.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        <ModeCard
          title="Mappa concettuale"
          description="Canvas con lenti di scoperta, inspector e suggerimenti serendipità — esplora collegamenti non ovvi."
          href="/research/canvas"
          cta="Apri mappa →"
          icon="map"
          isDisabled={!hasConcepts}
        />
        <ModeCard
          title="Esplorazione guidata"
          description="Trail lineare con basket — percorso curato nel grafo Knowledge."
          href="/research/guided"
          cta="Inizia trail →"
          icon="route"
        />
      </div>

      {!hasConcepts ? (
        <p className="text-sm text-ink-muted">
          Popola prima il grafo Knowledge per abilitare la mappa.{" "}
          <Link href="/knowledge" className="font-medium text-accent hover:underline cursor-pointer">
            Vai a Knowledge
          </Link>
          .
        </p>
      ) : (
        <section aria-label="Riprendi">
          <h2 className="text-sm font-medium text-ink">Riprendi</h2>
          <ResearchResumeSection />
        </section>
      )}
    </div>
  );
}
