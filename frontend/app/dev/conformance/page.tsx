import { ProgramTracePanel } from "@/components/conformance";
import { getProgramGraphObservation } from "@/lib/knowledgeClient";

export default async function ConformanceDevPage() {
  const graph = await getProgramGraphObservation();

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <ProgramTracePanel graph={graph} />
    </div>
  );
}
