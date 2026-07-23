import type { MemoryKind } from "@/lib/memoryClient";

const KIND_STYLES: Record<MemoryKind, string> = {
  user: "bg-blue-400/10 text-blue-300",
  thesis: "bg-violet-400/10 text-violet-300",
  editable: "bg-emerald-400/10 text-emerald-300",
  decision: "bg-amber-400/10 text-amber-300",
  concept: "bg-sky-400/10 text-sky-300",
  citation: "bg-rose-400/10 text-rose-300",
};

export function MemoryKindBadge({ kind }: { kind: MemoryKind }) {
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${KIND_STYLES[kind]}`}
      data-testid={`kind-badge-${kind}`}
    >
      {kind}
    </span>
  );
}
