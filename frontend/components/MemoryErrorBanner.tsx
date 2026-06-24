"use client";

type Props = {
  message: string | null;
  code?: string | null;
  status?: number | null;
};

export function MemoryErrorBanner({ message, code, status }: Props) {
  if (!message) return null;

  return (
    <div
      className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800"
      role="alert"
      data-testid="memory-error-banner"
    >
      {status ? `[${status}] ` : ""}
      {code ? `${code}: ` : ""}
      {message}
    </div>
  );
}
