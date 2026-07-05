"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  ExplainDefinitionBlock,
  ExplainHeaderBar,
  ExplainPageSkeleton,
  ExplainRegionWait,
} from "@/components/knowledge/explain";
import {
  supervisorAllowsDefinitionProgression,
  supervisorObservationLabel,
} from "@/components/knowledge/explain/supervisorObservation";
import {
  getConceptDefinition,
  getConceptHeader,
  getConformanceProjection,
} from "@/lib/knowledgeClient";
import type {
  ConceptDefinitionEnvelope,
  ConceptHeaderEnvelope,
  ConformanceProjection,
} from "@/lib/knowledgeTypes";

export type ExplainPageShellProps = {
  conceptSlug: string;
};

type PageState =
  | "loading"
  | "header_ready"
  | "wait_supervisor"
  | "ready"
  | "not_found"
  | "error";

/**
 * Explain Page — progressive load with Supervisor Interaction Observation (PX3-EWO-006).
 * Region A loads first; region B waits when §10 WAIT blocks progression (INV-R-16).
 */
export function ExplainPageShell({ conceptSlug }: ExplainPageShellProps) {
  const [pageState, setPageState] = useState<PageState>("loading");
  const [header, setHeader] = useState<ConceptHeaderEnvelope | null>(null);
  const [definition, setDefinition] = useState<ConceptDefinitionEnvelope | null>(
    null
  );
  const [projection, setProjection] = useState<ConformanceProjection | null>(
    null
  );
  const [waitMessage, setWaitMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDefinitionWhenAllowed(
      proj: ConformanceProjection | null
    ) {
      if (!supervisorAllowsDefinitionProgression(proj)) {
        setPageState("wait_supervisor");
        setWaitMessage(supervisorObservationLabel(proj));
        return;
      }
      setPageState("header_ready");
      try {
        const def = await getConceptDefinition(conceptSlug);
        if (cancelled) return;
        setDefinition(def);
        setPageState("ready");
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "";
        if (message === "concept_not_found") {
          setPageState("not_found");
          return;
        }
        setPageState("error");
      }
    }

    async function load() {
      setPageState("loading");
      setHeader(null);
      setDefinition(null);
      setWaitMessage(null);
      try {
        const [hdr, proj] = await Promise.all([
          getConceptHeader(conceptSlug),
          getConformanceProjection().catch(() => null),
        ]);
        if (cancelled) return;
        setHeader(hdr);
        setProjection(proj);
        await loadDefinitionWhenAllowed(proj);
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "";
        if (message === "concept_not_found") {
          setPageState("not_found");
          return;
        }
        setPageState("error");
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [conceptSlug]);

  useEffect(() => {
    if (pageState !== "wait_supervisor") return;
    if (supervisorAllowsDefinitionProgression(projection)) {
      void (async () => {
        try {
          const def = await getConceptDefinition(conceptSlug);
          setDefinition(def);
          setPageState("ready");
          setWaitMessage(null);
        } catch {
          setPageState("error");
        }
      })();
    }
  }, [pageState, projection, conceptSlug]);

  if (pageState === "loading") {
    return <ExplainPageSkeleton />;
  }

  if (pageState === "not_found") {
    return (
      <div className="mx-auto max-w-content" data-testid="explain-not-found">
        <h1 className="text-2xl font-semibold text-ink">Concetto non trovato</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Nessun concetto con slug{" "}
          <code className="font-mono text-xs">{conceptSlug}</code>.
        </p>
        <Link
          href="/knowledge"
          className="mt-4 inline-block text-sm font-medium text-accent underline-offset-2 hover:underline"
        >
          ← Torna a Knowledge
        </Link>
      </div>
    );
  }

  if (pageState === "error" || header == null) {
    return (
      <div className="mx-auto max-w-content" data-testid="explain-error">
        <p className="text-sm text-ink-muted">Errore nel caricamento del concetto.</p>
        <Link href="/knowledge" className="mt-4 inline-block text-sm text-accent hover:underline">
          ← Torna a Knowledge
        </Link>
      </div>
    );
  }

  const waveStatus =
    projection?.waves?.wave_b_supervisor?.status ??
    projection?.waves?.wave_b_projection?.status ??
    null;

  return (
    <div
      className="mx-auto max-w-content"
      data-testid={pageState === "ready" ? "explain-ready" : "explain-partial"}
    >
      <nav aria-label="Breadcrumb" className="mb-4">
        <Link
          href="/knowledge"
          className="text-sm font-medium text-accent underline-offset-2 hover:underline"
        >
          ← Knowledge
        </Link>
      </nav>

      {header.knowledge_state === "candidate" && (
        <p
          className="mb-4 rounded-md border border-dashed border-warning/40 bg-warning/5 px-3 py-2 text-xs text-warning"
          data-testid="explain-candidate-banner"
        >
          Candidato — definizione in revisione
        </p>
      )}

      {header.knowledge_state === "deprecated" && (
        <p
          className="mb-4 rounded-md border border-warning/30 bg-warning/10 px-3 py-2 text-sm text-warning"
          data-testid="explain-deprecated-banner"
        >
          Concetto deprecato
        </p>
      )}

      {waveStatus != null && (
        <p
          className="mb-4 text-xs text-ink-subtle"
          data-testid="explain-projection-status"
          title="Read-only program projection (SoR §9)"
        >
          Wave status (projection): {waveStatus}
        </p>
      )}

      {pageState === "wait_supervisor" && (
        <p
          className="mb-4 rounded-md border border-border bg-surface-muted px-3 py-2 text-xs text-ink-muted"
          data-testid="explain-supervisor-observation"
        >
          {waitMessage}
        </p>
      )}

      <ExplainHeaderBar header={header} />
      <div className="mt-6">
        {definition != null ? (
          <ExplainDefinitionBlock definition={definition} />
        ) : (
          <ExplainRegionWait message={waitMessage} />
        )}
      </div>
    </div>
  );
}
