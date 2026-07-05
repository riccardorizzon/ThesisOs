import { ExplainPageShell } from "@/components/knowledge/explain";

type Props = { params: Promise<{ conceptSlug: string }> };

export default async function KnowledgeConceptExplainPage({ params }: Props) {
  const { conceptSlug } = await params;
  return <ExplainPageShell conceptSlug={conceptSlug} />;
}
