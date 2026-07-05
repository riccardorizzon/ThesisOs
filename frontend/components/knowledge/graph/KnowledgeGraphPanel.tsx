"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { KnowledgeLifecycleBadge } from "@/components/knowledge/shared/KnowledgeBadges";
import { cn } from "@/lib/cn";
import type { KnowledgeGraphResponse, KnowledgeState } from "@/lib/knowledgeTypes";

export type KnowledgeGraphPanelProps = {
  graph: KnowledgeGraphResponse;
  className?: string;
};

function nodeBySlug(graph: KnowledgeGraphResponse, slug: string) {
  return graph.nodes.find((node) => node.slug === slug);
}

/**
 * Knowledge Graph §10 — bounded concept navigation with lifecycle badges (PX3-EWO-009).
 */
export function KnowledgeGraphPanel({ graph, className }: KnowledgeGraphPanelProps) {
  const [viewMode, setViewMode] = useState<"graph" | "list">(
    graph.limits.force_list_view ? "list" : graph.view_mode
  );

  const titleBySlug = useMemo(() => {
    const map = new Map<string, string>();
    for (const node of graph.nodes) {
      map.set(node.slug, node.title);
    }
    return map;
  }, [graph.nodes]);

  const showBanner =
    graph.limits.show_performance_banner || graph.limits.force_list_view;

  return (
    <div className={cn("space-y-4", className)} data-testid="knowledge-graph-panel">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Knowledge Graph</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Navigazione concetti — lifecycle badges (PX-3 §4), max{" "}
            {graph.limits.default_visible} nodi di default.
          </p>
          {graph.focus_slug != null && (
            <p className="mt-1 text-xs text-ink-subtle">
              Focus: <span className="font-mono">{graph.focus_slug}</span> · depth{" "}
              {graph.depth}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className={cn(
              "rounded-md border px-3 py-1.5 text-xs font-medium",
              viewMode === "graph"
                ? "border-accent bg-accent-subtle text-accent"
                : "border-border bg-surface text-ink-muted"
            )}
            onClick={() => setViewMode("graph")}
            disabled={graph.limits.force_list_view}
          >
            Grafo
          </button>
          <button
            type="button"
            className={cn(
              "rounded-md border px-3 py-1.5 text-xs font-medium",
              viewMode === "list"
                ? "border-accent bg-accent-subtle text-accent"
                : "border-border bg-surface text-ink-muted"
            )}
            onClick={() => setViewMode("list")}
          >
            Lista
          </button>
        </div>
      </header>

      {showBanner && (
        <p
          className="rounded-md border border-warning/30 bg-warning/5 px-3 py-2 text-sm text-warning"
          data-testid="graph-large-banner"
        >
          Grafo ampio — applica un filtro o passa alla lista
        </p>
      )}

      <p className="text-xs text-ink-subtle" data-testid="graph-node-count">
        {graph.limits.visible_count} / {graph.limits.total_in_scope} concetti visibili
        {graph.limits.truncated ? " (troncato)" : ""}
      </p>

      {viewMode === "list" ? (
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="min-w-full text-left text-sm" data-testid="graph-list-view">
            <thead className="border-b border-border bg-surface-muted text-xs uppercase text-ink-subtle">
              <tr>
                <th className="px-3 py-2">Concetto</th>
                <th className="px-3 py-2">Lifecycle (§4)</th>
                <th className="px-3 py-2">Grado</th>
                <th className="px-3 py-2">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {graph.nodes.map((node) => (
                <tr key={node.slug} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-medium text-ink">
                    {node.title}
                    {node.is_core && (
                      <span className="ml-2 text-xs text-accent">Core</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    <KnowledgeLifecycleBadge
                      state={node.knowledge_state as KnowledgeState}
                    />
                  </td>
                  <td className="px-3 py-2 text-ink-muted">{node.degree}</td>
                  <td className="px-3 py-2">
                    <Link
                      href={`/knowledge/${node.slug}`}
                      className="text-xs text-accent hover:underline"
                    >
                      Apri
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <>
          <div
            className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
            data-testid="graph-node-grid"
          >
            {graph.nodes.map((node) => (
              <article
                key={node.slug}
                className={cn(
                  "rounded-md border border-border bg-surface p-3 shadow-sm",
                  graph.focus_slug === node.slug && "border-accent ring-1 ring-accent/30"
                )}
                data-testid={`graph-node-${node.slug}`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  {node.is_core && (
                    <span className="rounded-full bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent">
                      Core
                    </span>
                  )}
                  <KnowledgeLifecycleBadge
                    state={node.knowledge_state as KnowledgeState}
                  />
                </div>
                <h3 className="mt-2 text-sm font-semibold text-ink">{node.title}</h3>
                <p className="mt-1 text-xs text-ink-subtle">{node.degree} collegamenti</p>
                <Link
                  href={`/knowledge/${node.slug}`}
                  className="mt-2 inline-block text-xs font-medium text-accent hover:underline"
                >
                  Apri concetto
                </Link>
              </article>
            ))}
          </div>

          {graph.edges.length > 0 && (
            <section data-testid="graph-edge-list">
              <h2 className="text-sm font-semibold text-ink">Relazioni visibili</h2>
              <ul className="mt-2 space-y-1 text-xs text-ink-muted">
                {graph.edges.map((edge) => (
                  <li key={`${edge.source}-${edge.target}`}>
                    {titleBySlug.get(edge.source) ?? edge.source} ↔{" "}
                    {titleBySlug.get(edge.target) ?? edge.target}
                    <span className="text-ink-subtle"> ({edge.relation})</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}

      <nav aria-label="Knowledge navigation">
        <Link
          href="/knowledge"
          className="text-sm font-medium text-accent underline-offset-2 hover:underline"
        >
          ← Torna a Knowledge
        </Link>
      </nav>
    </div>
  );
}

export { nodeBySlug };
