import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import {
  JobFsmObservationStrip,
  KnowledgeGraphPanel,
} from "./index";
import type { JobFsmObservation, KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

const SAMPLE_GRAPH: KnowledgeGraphResponse = {
  schema_version: 1,
  focus_slug: "aura",
  depth: 1,
  view_mode: "graph",
  nodes: [
    {
      id: "aura",
      slug: "aura",
      title: "Aura",
      knowledge_state: "validated",
      is_core: true,
      degree: 1,
    },
    {
      id: "riproducibilita",
      slug: "riproducibilita",
      title: "Riproducibilità tecnica",
      knowledge_state: "validated",
      is_core: false,
      degree: 1,
    },
  ],
  edges: [{ source: "aura", target: "riproducibilita", relation: "related" }],
  limits: {
    default_visible: 15,
    soft_limit: 50,
    hard_limit: 100,
    visible_count: 2,
    total_in_scope: 7,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

const SAMPLE_JOB_FSM: JobFsmObservation = {
  schema_version: 1,
  read_only: true,
  source: "conformance/projection",
  vocabulary_domains: [
    {
      domain: "product_lifecycle",
      vocabulary: "PX-3 §4",
      values: ["candidate", "validated"],
      notes: "Product lifecycle",
    },
    {
      domain: "mb2_aggregate",
      vocabulary: "SoR §5.3",
      values: ["waiting", "running", "pass"],
      notes: "Aggregate",
    },
    {
      domain: "mb2_job_fsm",
      vocabulary: "SoR §5.1",
      values: ["READY", "RUNNING", "DONE"],
      notes: "Job FSM",
    },
  ],
  aggregate_to_job_fsm: [
    { aggregate_status: "running", job_fsm_subset: "RUNNING", display_label: "Active" },
  ],
  projection_jobs: [
    {
      ewo_id: "PX3-EWO-008",
      aggregate_status: "pass",
      job_fsm_subset: "DONE",
      wave_id: "wave_c_execution_graph",
    },
  ],
  inv_r_11_note: "Projection is read-only (INV-R-11).",
};

afterEach(() => {
  cleanup();
});

describe("KnowledgeGraphPanel", () => {
  it("renders lifecycle badges on concept nodes", () => {
    render(<KnowledgeGraphPanel graph={SAMPLE_GRAPH} />);
    const auraNode = screen.getByTestId("graph-node-aura");
    expect(auraNode).toBeTruthy();
    expect(auraNode.querySelector('[data-testid="knowledge-state-validated"]')).toBeTruthy();
    expect(screen.getByTestId("graph-edge-list")).toHaveTextContent("Aura");
  });

  it("switches to list view", () => {
    render(<KnowledgeGraphPanel graph={SAMPLE_GRAPH} />);
    fireEvent.click(screen.getByRole("button", { name: "Lista" }));
    expect(screen.getByTestId("graph-list-view")).toBeTruthy();
  });
});

describe("JobFsmObservationStrip", () => {
  it("labels MB2 Job FSM separately from lifecycle", () => {
    render(<JobFsmObservationStrip observation={SAMPLE_JOB_FSM} />);
    expect(screen.getByTestId("job-fsm-observation")).toHaveTextContent(
      "Job FSM (projection)"
    );
    expect(screen.getByTestId("vocabulary-domains")).toHaveTextContent(
      "Product lifecycle"
    );
    expect(screen.getByTestId("job-fsm-projection-list")).toHaveTextContent(
      "PX3-EWO-008"
    );
  });
});
