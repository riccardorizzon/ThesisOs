import Link from "next/link";
import { ContextBar } from "@/components/context";
import { ModuleStub } from "@/components/ModuleStub";
import { loadContext } from "@/lib/contextLoad";

export default async function WritingPage() {
  const context = await loadContext();

  return (
    <div className="space-y-6">
      <ContextBar packet={context} />
      <ModuleStub
        title="Writing"
        milestone="PX-2"
        description="Layout fisso a tre pannelli: outline, editor Markdown, pannello azioni AI."
      >
        <p className="text-sm text-ink-muted">
          L&apos;editor arriva in PX-2. I capitoli promossi restano accessibili via API.
          Torna alla{" "}
          <Link href="/" className="font-medium text-accent hover:underline cursor-pointer">
            Home
          </Link>{" "}
          per continuare l&apos;ultimo capitolo.
        </p>
      </ModuleStub>
    </div>
  );
}
