import { KnowledgeView } from "@/components/library/KnowledgeView";
import { LIBRARY_CONCEPTS } from "@/lib/libraryStub";

export default function KnowledgePage() {
  return <KnowledgeView concepts={LIBRARY_CONCEPTS} />;
}
