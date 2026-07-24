import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { BibliographyExportBar } from "@/components/sources/BibliographyExportBar";

afterEach(cleanup);

describe("BibliographyExportBar", () => {
  it("explains why export is empty when only candidate sources exist", () => {
    render(<BibliographyExportBar approvedCount={0} candidateCount={2} />);

    expect(
      screen.getByText(
        "Aggiungi almeno una fonte candidata alla bibliografia per esportarla."
      )
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Esporta BibTeX" })
    ).toBeDisabled();
  });

  it("enables export when an approved source exists", () => {
    render(<BibliographyExportBar approvedCount={1} candidateCount={0} />);
    expect(
      screen.getByRole("button", { name: "Esporta BibTeX" })
    ).toBeEnabled();
  });
});
