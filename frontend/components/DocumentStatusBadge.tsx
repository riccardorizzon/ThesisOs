import type { DocumentStatus } from "@/lib/documentClient";

const STATUS_STYLES: Record<DocumentStatus, string> = {
  uploaded: "bg-gray-100 text-gray-700",
  processing: "bg-amber-100 text-amber-800",
  parsed: "bg-emerald-100 text-emerald-800",
  failed: "bg-rose-100 text-rose-800",
};

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  const style = STATUS_STYLES[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${style}`}
      data-testid={`status-badge-${status}`}
    >
      {status}
    </span>
  );
}
