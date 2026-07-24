import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DeleteProjectPanel } from "@/components/settings/DeleteProjectPanel";
import { deleteProject } from "@/lib/projectsClient";
import {
  clearProjectBrowserState,
  setActiveProjectId,
} from "@/lib/projectPrefs";

const replace = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, refresh }),
}));

vi.mock("@/lib/projectsClient", () => ({
  deleteProject: vi.fn(),
}));

vi.mock("@/lib/projectPrefs", () => ({
  clearProjectBrowserState: vi.fn(),
  setActiveProjectId: vi.fn(),
}));

vi.mock("@/lib/workspacePrefs", () => ({
  setWorkspaceMode: vi.fn(),
}));

beforeEach(() => {
  vi.mocked(deleteProject).mockResolvedValue(undefined);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("DeleteProjectPanel", () => {
  it.each(["thesis-agent", "demo-thesis"])(
    "does not expose deletion for protected project %s",
    (projectId) => {
      render(
        <DeleteProjectPanel
          projectId={projectId}
          displayName="Progetto protetto"
        />
      );

      expect(
        screen.queryByRole("button", {
          name: "Elimina definitivamente questa tesi",
        })
      ).not.toBeInTheDocument();
    }
  );

  it("requires opening the dialog and typing the exact project id", async () => {
    render(
      <DeleteProjectPanel
        projectId="thesis-002"
        displayName="Tesi eliminabile"
      />
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Elimina definitivamente questa tesi",
      })
    );
    const confirm = screen.getByRole("button", {
      name: "Conferma eliminazione definitiva",
    });
    expect(confirm).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Digita thesis-002 per confermare"), {
      target: { value: "thesis-002" },
    });
    expect(confirm).toBeEnabled();
    fireEvent.click(confirm);

    await waitFor(() => {
      expect(deleteProject).toHaveBeenCalledWith("thesis-002", "thesis-002");
    });
    expect(clearProjectBrowserState).toHaveBeenCalledWith("thesis-002");
    expect(setActiveProjectId).toHaveBeenCalledWith("thesis-agent");
    expect(replace).toHaveBeenCalledWith("/");
  });

  it("keeps the project active and reports deletion errors", async () => {
    vi.mocked(deleteProject).mockRejectedValue(
      new Error("Eliminazione non riuscita. Riprova.")
    );
    render(
      <DeleteProjectPanel
        projectId="thesis-002"
        displayName="Tesi eliminabile"
      />
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Elimina definitivamente questa tesi",
      })
    );
    fireEvent.change(screen.getByLabelText("Digita thesis-002 per confermare"), {
      target: { value: "thesis-002" },
    });
    fireEvent.click(
      screen.getByRole("button", {
        name: "Conferma eliminazione definitiva",
      })
    );

    expect(
      await screen.findByText("Eliminazione non riuscita. Riprova.")
    ).toBeInTheDocument();
    expect(clearProjectBrowserState).not.toHaveBeenCalled();
    expect(setActiveProjectId).not.toHaveBeenCalled();
    expect(replace).not.toHaveBeenCalled();
  });
});
