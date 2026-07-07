"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { KnowledgeLifecycleBadge } from "@/components/knowledge/shared/KnowledgeBadges";
import { cn } from "@/lib/cn";
import { CONFIDENCE_LABELS } from "@/lib/knowledgeTypes";
import { getKnowledgeObject } from "@/lib/knowledgeClient";
import type { KnowledgeGraphResponse, KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

export type InspectorTabId = "dettaglio" | "collegamenti" | "azioni";

const INSPECTOR_TABS: Array<{ id: InspectorTabId; label: string }> = [
  { id: "dettaglio", label: "Dettaglio" },
  { id: "collegamenti", label: "Collegamenti" },
  { id: "azioni", label: "Azioni" },
];

export type ResearchInspectorRailProps = {
  selectedSlugs: readonly string[];
  graph: KnowledgeGraphResponse;
  className?: string;
  onAddToBasket?: (slugs: readonly string[]) => void;
};

function relatedConceptLinks(graph: KnowledgeGraphResponse, slug: string): string[] {
  const related = new Set<string>();
  for (const edge of graph.edges) {
    if (edge.source === slug) related.add(edge.target);
    if (edge.target === slug) related.add(edge.source);
  }
  return [...related];
}

/**
 * Canvas inspector rail — summary tabs for selected concept (PX5-EWO-005).
 * Layer: Business (Product Plane)
 */
export function ResearchInspectorRail({
  selectedSlugs,
  graph,
  className,
  onAddToBasket,
}: ResearchInspectorRailProps) {
  const [activeTab, setActiveTab] = useState<InspectorTabId>("dettaglio");
  const [detail, setDetail] = useState<KnowledgeObjectEnvelope | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const singleSlug = selectedSlugs.length === 1 ? selectedSlugs[0] : null;

  useEffect(() => {
    if (singleSlug == null) {
      setDetail(null);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    getKnowledgeObject(singleSlug)
      .then((envelope) => {
        if (!cancelled) setDetail(envelope);
      })
      .catch(() => {
        if (!cancelled) {
          setDetail(null);
          setError("Impossibile caricare il concetto.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [singleSlug]);

  if (selectedSlugs.length === 0) {
    return (
      <div className={cn("flex h-full flex-col", className)} data-testid="canvas-inspector-empty">
        <p className="text-sm text-ink-muted">Seleziona un nodo sulla mappa.</p>
      </div>
    );
  }

  if (selectedSlugs.length > 1) {
    return (
      <div className={cn("flex h-full flex-col gap-3", className)} data-testid="canvas-inspector-multi">
        <p className="text-sm font-medium text-ink">
          {selectedSlugs.length} nodi selezionati
        </p>
        <button
          type="button"
          disabled={onAddToBasket == null}
          className="rounded-md border border-border px-3 py-1.5 text-sm text-ink hover:bg-surface-muted cursor-pointer disabled:text-ink-subtle"
          data-testid="canvas-inspector-batch-basket"
          onClick={() => onAddToBasket?.(selectedSlugs)}
        >
          Aggiungi al basket
        </button>
      </div>
    );
  }

  const slug = singleSlug!;
  const related = relatedConceptLinks(graph, slug);

  return (
    <div className={cn("flex h-full flex-col", className)} data-testid="canvas-inspector-rail">
      <div role="tablist" aria-label="Inspector canvas" className="flex border-b border-border">
        {INSPECTOR_TABS.map((tab) => {
          const selected = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex-1 px-2 py-2 text-xs font-medium cursor-pointer",
                selected ? "border-b-2 border-accent text-ink" : "text-ink-muted"
              )}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto p-3 text-sm" role="tabpanel">
        {loading && <p className="text-ink-muted">Caricamento…</p>}
        {error != null && <p className="text-warning">{error}</p>}

        {!loading && activeTab === "dettaglio" && detail != null && (
          <div className="space-y-3" data-testid="canvas-inspector-dettaglio">
            <div>
              <h2 className="font-semibold text-ink">{detail.title}</h2>
              {detail.subtitle != null && (
                <p className="text-xs text-ink-subtle">{detail.subtitle}</p>
              )}
            </div>
            <KnowledgeLifecycleBadge state={detail.knowledge_state} />
            <p className="text-xs text-ink-muted">
              Confidenza: {CONFIDENCE_LABELS[detail.confidence]}
            </p>
            {detail.summary != null && detail.summary.length > 0 && (
              <p className="text-ink-muted">{detail.summary}</p>
            )}
          </div>
        )}

        {!loading && activeTab === "dettaglio" && detail == null && error == null && (
          <div data-testid="canvas-inspector-dettaglio-fallback">
            <h2 className="font-semibold text-ink">
              {graph.nodes.find((node) => node.slug === slug)?.title ?? slug}
            </h2>
            <p className="mt-2 text-ink-muted">Riepilogo concetto — apri Explain per il dettaglio canonico.</p>
          </div>
        )}

        {activeTab === "collegamenti" && (
          <div className="space-y-3" data-testid="canvas-inspector-collegamenti">
            {related.length > 0 && (
              <div>
                <p className="text-xs font-medium uppercase text-ink-subtle">Concetti</p>
                <ul className="mt-1 space-y-1">
                  {related.map((relatedSlug) => (
                    <li key={relatedSlug}>
                      <Link
                        href={`/knowledge/${relatedSlug}`}
                        className="text-accent hover:underline"
                      >
                        {graph.nodes.find((node) => node.slug === relatedSlug)?.title ?? relatedSlug}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {detail != null && detail.linked_counts.sources > 0 && (
              <div>
                <p className="text-xs font-medium uppercase text-ink-subtle">Fonti</p>
                <ul className="mt-1 space-y-1">
                  {Array.from({ length: detail.linked_counts.sources }).map((_, index) => (
                    <li key={index}>
                      <Link href="/sources" className="text-accent hover:underline">
                        Fonte collegata {index + 1}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {detail != null && detail.linked_counts.chapters > 0 && (
              <Link href="/writing" className="text-accent hover:underline">
                Capitoli collegati ({detail.linked_counts.chapters})
              </Link>
            )}
            <Link
              href={`/knowledge/graph?focus=${encodeURIComponent(slug)}&depth=1`}
              className="inline-block text-accent hover:underline"
            >
              Apri grafo Knowledge
            </Link>
          </div>
        )}

        {activeTab === "azioni" && (
          <div className="space-y-2" data-testid="canvas-inspector-azioni">
            <Link
              href={`/knowledge/${slug}`}
              className="inline-flex rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-on-accent hover:opacity-90"
              data-testid="canvas-inspector-explain-link"
            >
              Apri Explain
            </Link>
            <button
              type="button"
              className="block rounded-md border border-border px-3 py-1.5 text-sm text-ink hover:bg-surface-muted cursor-pointer"
              data-testid="canvas-inspector-basket-button"
              onClick={() => onAddToBasket?.([slug])}
            >
              Aggiungi al basket
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
