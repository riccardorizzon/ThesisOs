import { ModuleStub } from "@/components/ModuleStub";

type Props = { params: Promise<{ conceptId: string }> };

export default async function ResearchConceptPage({ params }: Props) {
  const { conceptId } = await params;
  return (
    <ModuleStub
      title={`Research — ${conceptId}`}
      milestone="PX-5"
      description="Dettaglio concetto nel grafo di ricerca."
    />
  );
}
