"use client";

type Props = {
  message: string | null;
  code?: string | null;
  status?: number | null;
};

export function DocumentErrorBanner({ message, code, status }: Props) {
  if (!message) return null;

  return (
    <div
      className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger"
      role="alert"
      data-testid="document-error-banner"
    >
      {status ? `[${status}] ` : ""}
      {code ? `${code}: ` : ""}
      {message}
    </div>
  );
}
