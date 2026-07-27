import { ManuscriptWorkspace } from "@/components/manuscript";

type Props = { params: Promise<{ chapterId: string }> };

export default async function ManuscriptChapterPage({ params }: Props) {
  const { chapterId } = await params;
  return <ManuscriptWorkspace chapterId={chapterId} />;
}
