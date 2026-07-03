import { SourcesView } from "@/components/library/SourcesView";
import { LIBRARY_SOURCES } from "@/lib/libraryStub";

export default function SourcesPage() {
  return <SourcesView sources={LIBRARY_SOURCES} />;
}
