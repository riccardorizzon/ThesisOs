import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DocumentStatusBadge } from "@/components/DocumentStatusBadge";
import type { DocumentStatus } from "@/lib/documentClient";

const STATUSES: DocumentStatus[] = ["uploaded", "processing", "parsed", "failed"];

describe("DocumentStatusBadge", () => {
  it.each(STATUSES)("renders the %s status", (status) => {
    render(<DocumentStatusBadge status={status} />);
    expect(screen.getByTestId(`status-badge-${status}`)).toHaveTextContent(status);
  });
});
