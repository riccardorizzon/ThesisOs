import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InputBox } from "@/components/InputBox";

afterEach(cleanup);

describe("InputBox", () => {
  it("caps chat input at the backend limit and explains the limit", () => {
    render(<InputBox disabled={false} onSend={vi.fn()} />);
    const input = screen.getByPlaceholderText("Scrivi un messaggio…");

    expect(input).toHaveAttribute("maxLength", "32000");
    fireEvent.change(input, { target: { value: "x".repeat(32_001) } });

    expect(input).toHaveValue("x".repeat(32_000));
    expect(
      screen.getByText("Limite di 32.000 caratteri raggiunto.")
    ).toBeInTheDocument();
  });

  it("replaces send with cancel while streaming", () => {
    const onCancel = vi.fn();
    render(
      <InputBox
        disabled={false}
        streaming
        onCancel={onCancel}
        onSend={vi.fn()}
      />
    );

    expect(screen.queryByRole("button", { name: "Invia" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Interrompi" }));
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
