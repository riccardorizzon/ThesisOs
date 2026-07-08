import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { ApiErrorBanner } from "./ApiErrorBanner";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

afterEach(() => {
  cleanup();
  refresh.mockClear();
});

describe("ApiErrorBanner", () => {
  it("renders title and message", () => {
    render(
      <ApiErrorBanner title="Errore" message="Backend non raggiungibile" />
    );
    expect(screen.getByText("Errore")).toBeTruthy();
    expect(screen.getByTestId("api-error-banner-message")).toHaveTextContent(
      "Backend non raggiungibile"
    );
  });

  it("calls router.refresh on retry by default", () => {
    render(<ApiErrorBanner title="Errore" message="Retry me" />);
    fireEvent.click(screen.getByTestId("api-error-banner-retry"));
    expect(refresh).toHaveBeenCalled();
  });

  it("uses custom onRetry when provided", () => {
    const onRetry = vi.fn();
    render(
      <ApiErrorBanner title="Errore" message="Custom" onRetry={onRetry} />
    );
    fireEvent.click(screen.getByTestId("api-error-banner-retry"));
    expect(onRetry).toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();
  });
});
