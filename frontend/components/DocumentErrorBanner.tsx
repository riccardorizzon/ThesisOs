"use client";

type Props = {
  message: string | null;
  code?: string | null;
  status?: number | null;
};

const ERROR_COPY: Readonly<Record<string, string>> = {
  unsupported_format:
    "Formato non supportato. Usa PDF, EPUB, DOCX, Markdown o testo.",
  invalid_file_content:
    "Il contenuto del file non corrisponde al formato selezionato.",
  document_not_found: "Il documento non è più disponibile.",
  write_conflict:
    "Il documento è stato modificato altrove. Ricarica e riprova.",
  parser_unavailable:
    "Questo formato non può essere analizzato in questo momento.",
  parse_failed:
    "Il documento non può essere analizzato. Controlla il file e riprova.",
};

export function DocumentErrorBanner({ message, code }: Props) {
  if (!message) return null;
  const productMessage =
    (code ? ERROR_COPY[code] : null) ??
    "Operazione sul documento non riuscita. Riprova.";

  return (
    <div
      className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger"
      role="alert"
      data-testid="document-error-banner"
    >
      {productMessage}
    </div>
  );
}
