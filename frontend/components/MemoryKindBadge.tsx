import type { MemoryKind } from "@/lib/memoryClient";

const KIND_STYLES: Record<MemoryKind, string> = {
  user: "bg-blue-100 text-blue-800",
  thesis: "bg-violet-100 text-violet-800",
  editable: "bg-emerald-100 text-emerald-800",
  decision: "bg-amber-100 text-amber-800",
  concept: "bg-sky-100 text-sky-800",
  citation: "bg-rose-100 text-rose-800",
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
