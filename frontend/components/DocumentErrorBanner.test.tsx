import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";

afterEach(cleanup);

describe("DocumentErrorBanner", () => {
  it("maps invalid file content without exposing parser details", () => {
    render(
      <DocumentErrorBanner
        status={415}
        code="invalid_file_content"
        message="pymupdf could not open PDF: Failed to open stream"
      />
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent(
      "Il contenuto del file non corrisponde al formato selezionato."
    );
    expect(alert).not.toHaveTextContent(/pymupdf|Failed to open|415/i);
  });

  it("uses generic product copy for unknown technical errors", () => {
    render(
      <DocumentErrorBanner
        message={`Unexpected token '<', "<!DOCTYPE "... is not valid JSON`}
      />
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent(
      "Operazione sul documento non riuscita. Riprova."
    );
    expect(alert).not.toHaveTextContent(/Unexpected token|DOCTYPE/i);
  });
});
