import type { DocumentStatus } from "@/lib/documentClient";

const STATUS_STYLES: Record<DocumentStatus, string> = {
  uploaded: "bg-surface-muted text-ink-muted",
  processing: "bg-warning/10 text-warning",
  parsed: "bg-success/10 text-success",
  failed: "bg-danger/10 text-danger",
};

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  const style = STATUS_STYLES[status] ?? "bg-surface-muted text-ink-muted";
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${style}`}
      data-testid={`status-badge-${status}`}
    >
      {status}
    </span>
  );
}
