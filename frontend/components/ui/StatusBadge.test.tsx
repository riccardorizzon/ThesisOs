import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  it.each([
    ["draft", "Bozza"],
    ["review", "In revisione"],
    ["approved", "Approvato"],
  ] as const)("renders %s as %s", (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(label)).toBeTruthy();
    expect(screen.getByTestId(`status-badge-${status}`)).toBeTruthy();
  });
});
