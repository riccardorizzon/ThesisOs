import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { EntityCard } from "./EntityCard";

describe("EntityCard", () => {
  it("renders entity type label and title", () => {
    render(
      <EntityCard entityType="source" title="Benjamin — Opera d'arte" subtitle="Libro" />
    );
    expect(screen.getByText("Fonte")).toBeTruthy();
    expect(screen.getByText("Benjamin — Opera d'arte")).toBeTruthy();
    expect(screen.getByText("Libro")).toBeTruthy();
  });

  it("renders as link when href provided", () => {
    render(
      <EntityCard
        entityType="chapter"
        title="Cap. 1"
        href="/writing/1"
        meta="Bozza"
      />
    );
    const link = screen.getByRole("link", { name: /Capitolo/i });
    expect(link.getAttribute("href")).toBe("/writing/1");
    expect(screen.getByText("Bozza")).toBeTruthy();
  });

  it("renders as article without href", () => {
    const { container } = render(
      <EntityCard entityType="concept" title="STIGMATA" />
    );
    expect(container.querySelector("article")).toBeTruthy();
    expect(screen.getByText("Concetto")).toBeTruthy();
  });
});
