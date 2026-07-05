import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import { ExplainPageShell } from "./ExplainPageShell";
import {
  supervisorAllowsDefinitionProgression,
  supervisorObservationLabel,
} from "./supervisorObservation";
import type {
  ConceptDefinitionEnvelope,
  ConceptHeaderEnvelope,
  ConformanceProjection,
} from "@/lib/knowledgeTypes";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

vi.mock("@/lib/knowledgeClient", () => ({
  getConceptHeader: vi.fn(),
  getConceptDefinition: vi.fn(),
  getConformanceProjection: vi.fn(),
}));

import {
  getConceptDefinition,
  getConceptHeader,
  getConformanceProjection,
} from "@/lib/knowledgeClient";

const HEADER: ConceptHeaderEnvelope = {
  id: "aura",
  slug: "aura",
  title: "Aura",
  subtitle: "Benjamin",
  confidence: "alta",
  knowledge_state: "validated",
  is_core: true,
};

const DEFINITION: ConceptDefinitionEnvelope = {
  slug: "aura",
  definition: "Presenza unica dell'oggetto nel tempo e nello spazio.",
  source_count: 1,
};

const PROJECTION_WAIT: ConformanceProjection = {
  schema_version: 1,
  program_id: "thesisos-product-v2",
  derived_at: "2026-07-05T00:00:00Z",
  supervisor: { state: "WAIT", reason: "Architect review gate" },
  waves: {
    wave_b_supervisor: {
      status: "waiting",
      jobs: { "PX3-EWO-006": { status: "waiting" } },
    },
  },
  gates: { ci: "unknown", coverage: "pass" },
};

const PROJECTION_CLEARED: ConformanceProjection = {
  ...PROJECTION_WAIT,
  waves: {
    wave_b_supervisor: {
      status: "running",
      jobs: { "PX3-EWO-006": { status: "running" } },
    },
  },
};

afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});

describe("supervisorObservation", () => {
  it("blocks definition progression under WAIT without delegation", () => {
    expect(supervisorAllowsDefinitionProgression(PROJECTION_WAIT)).toBe(false);
    expect(supervisorObservationLabel(PROJECTION_WAIT)).toContain("WAIT");
  });

  it("allows progression when wave job is running", () => {
    expect(supervisorAllowsDefinitionProgression(PROJECTION_CLEARED)).toBe(true);
  });
});

describe("ExplainPageShell progressive load", () => {
  it("loads region B after supervisor gate clears", async () => {
    vi.mocked(getConceptHeader).mockResolvedValue(HEADER);
    vi.mocked(getConceptDefinition).mockResolvedValue(DEFINITION);
    vi.mocked(getConformanceProjection).mockResolvedValue(PROJECTION_CLEARED);

    render(<ExplainPageShell conceptSlug="aura" />);

    await waitFor(() => {
      expect(screen.getByTestId("explain-ready")).toBeTruthy();
    });

    expect(screen.getByTestId("explain-region-a")).toHaveTextContent("Aura");
    expect(screen.getByTestId("explain-region-b")).toHaveTextContent("Presenza unica");
  });

  it("halts region B under supervisor WAIT (INV-R-16 observation)", async () => {
    vi.mocked(getConceptHeader).mockResolvedValue(HEADER);
    vi.mocked(getConformanceProjection).mockResolvedValue(PROJECTION_WAIT);

    render(<ExplainPageShell conceptSlug="aura" />);

    await waitFor(() => {
      expect(screen.getByTestId("explain-partial")).toBeTruthy();
    });

    expect(screen.getByTestId("explain-region-a")).toHaveTextContent("Aura");
    expect(screen.getByTestId("explain-region-b-wait")).toBeTruthy();
    expect(screen.getByTestId("explain-supervisor-observation")).toBeTruthy();
    expect(getConceptDefinition).not.toHaveBeenCalled();
  });
});
