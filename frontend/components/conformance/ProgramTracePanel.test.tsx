import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProgramTracePanel } from "./ProgramTracePanel";
import type { ProgramGraphObservation } from "@/lib/knowledgeTypes";

const SAMPLE_GRAPH: ProgramGraphObservation = {
  schema_version: 1,
  program_id: "px3-parallel",
  parent_program: "thesisos-product-v2",
  source: ".asep/programs/px3-parallel.yaml",
  waves: [
    {
      wave_id: "wave_c_execution_graph",
      title: "Execution Graph Observation (§4.2)",
      depends_on_wave: "wave_b_conformance_integration",
      execute_in_parallel: false,
      merge_order: [],
      workorders: ["PX3-EWO-008"],
      unblocks: "wave_c_job_fsm",
      wave_type: null,
      status: null,
      sub_agents: { "PX3-EWO-008": "A" },
      nodes: [
        {
          node_id: "PX3-EWO-008",
          node_type: "ewo",
          wave_id: "wave_c_execution_graph",
        },
      ],
    },
  ],
  edges: [
    {
      source: "wave_b_conformance_integration",
      target: "wave_c_execution_graph",
      edge_type: "depends_on_wave",
    },
  ],
};

describe("ProgramTracePanel", () => {
  it("renders wave DAG and INV-R-12 boundary", () => {
    render(<ProgramTracePanel graph={SAMPLE_GRAPH} />);

    expect(screen.getByTestId("program-trace-panel")).toBeInTheDocument();
    expect(screen.getByTestId("inv-r-12-boundary")).toHaveTextContent(
      "no ReadySet"
    );
    expect(screen.getByTestId("wave-wave_c_execution_graph")).toBeInTheDocument();
    expect(screen.getByTestId("node-PX3-EWO-008")).toBeInTheDocument();
    expect(screen.getByTestId("wave-edge")).toHaveTextContent(
      "wave_b_conformance_integration → wave_c_execution_graph"
    );
  });
});
