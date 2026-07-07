import { redirect } from "next/navigation";

type Props = { params: Promise<{ conceptId: string }> };

export default async function ResearchConceptPage({ params }: Props) {
  const { conceptId } = await params;
  redirect(`/research/canvas?focus=${encodeURIComponent(conceptId)}`);
}
