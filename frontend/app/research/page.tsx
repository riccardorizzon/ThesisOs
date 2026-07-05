import Link from "next/link";
import { ModuleStub } from "@/components/ModuleStub";

export default function ResearchPage() {
  return (
    <ModuleStub
      title="Research"
      milestone="PX-5"
      description="Mappa interattiva del panorama concettuale — nodi collegati a fonti, capitoli e decisioni."
    >
      <p className="text-sm text-ink-muted">
        Richiede il grafo Knowledge popolato (PX-4). Intanto esplora{" "}
        <Link href="/knowledge" className="font-medium text-accent hover:underline cursor-pointer">
          Knowledge
        </Link>{" "}
        o avvia una{" "}
        <Link href="/ai" className="font-medium text-accent hover:underline cursor-pointer">
          sessione AI
        </Link>
        .
      </p>
    </ModuleStub>
  );
}
