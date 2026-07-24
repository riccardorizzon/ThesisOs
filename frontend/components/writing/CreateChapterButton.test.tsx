import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";

import { CreateChapterButton } from "./CreateChapterButton";
import { chapterClient } from "@/lib/chapterClient";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    create: vi.fn(),
  },
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("CreateChapterButton", () => {
  beforeEach(() => {
    vi.mocked(chapterClient.create).mockResolvedValue({
      id: "new-ch",
      parent_id: null,
      order_index: 0,
      title: "Introduzione",
      status: "draft",
      content_md: null,
      summary: null,
      word_count: 0,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });
  });

  it("opens title form from primary CTA", () => {
    render(<CreateChapterButton />);

    fireEvent.click(screen.getByTestId("writing-create-chapter-cta"));
    expect(screen.getByTestId("writing-create-chapter-form")).toBeTruthy();
    expect(screen.getByTestId("writing-create-chapter-title")).toHaveValue("Introduzione");
  });

  it("creates chapter and navigates to editor", async () => {
    const onCreated = vi.fn();
    render(<CreateChapterButton onCreated={onCreated} />);

    fireEvent.click(screen.getByTestId("writing-create-chapter-cta"));
    fireEvent.click(screen.getByTestId("writing-create-chapter-submit"));

    await waitFor(() => {
      expect(chapterClient.create).toHaveBeenCalledWith({
        project_id: "thesis-agent",
        title: "Introduzione",
      });
    });
    expect(onCreated).toHaveBeenCalledWith(expect.objectContaining({ id: "new-ch" }));
    expect(push).toHaveBeenCalledWith("/writing/new-ch");
  });

  it("renders icon variant for outline header", () => {
    render(<CreateChapterButton variant="icon" testId="writing-outline-add-chapter" />);

    expect(screen.getByTestId("writing-outline-add-chapter")).toHaveAttribute(
      "aria-label",
      "Crea capitolo"
    );
  });

  it("enforces the 200 character title contract before submitting", async () => {
    render(<CreateChapterButton />);
    fireEvent.click(screen.getByTestId("writing-create-chapter-cta"));
    const input = screen.getByTestId("writing-create-chapter-title");

    expect(input).toHaveAttribute("maxLength", "200");
    fireEvent.change(input, { target: { value: "A".repeat(201) } });
    fireEvent.click(screen.getByTestId("writing-create-chapter-submit"));

    expect(
      await screen.findByText("Il titolo può contenere al massimo 200 caratteri.")
    ).toBeInTheDocument();
    expect(chapterClient.create).not.toHaveBeenCalled();
  });
});
