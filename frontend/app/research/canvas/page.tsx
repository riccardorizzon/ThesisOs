import { ResearchCanvasStub } from "@/components/research/ResearchCanvasStub";

type Props = {
  searchParams: Promise<{ focus?: string; view?: string }>;
};

export default async function ResearchCanvasPage({ searchParams }: Props) {
  const params = await searchParams;
  return <ResearchCanvasStub focus={params.focus} view={params.view} />;
}
