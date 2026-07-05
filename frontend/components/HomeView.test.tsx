import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup, waitFor } from "@testing-library/react";
import { HomeView } from "./HomeView";
import { PROPOSALS_STORAGE_KEY, SESSION_STATE_STORAGE_KEY } from "@/lib/sessionState";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    className,
    ...rest
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
  }) => (
    <a href={href} className={className} {...rest}>
      {children}
    </a>
  ),
}));

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe("HomeView", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders progress, continue, quick actions, and activity", () => {
    render(
      <HomeView
        progressPct={46}
        continueTarget={{ href: "/writing/2", label: "Cap. 2" }}
        activity={[
          {
            entityType: "chapter",
            title: "Cap. 2",
            subtitle: "In revisione",
            href: "/writing/2",
          },
        ]}
      />
    );

    expect(screen.getByRole("heading", { name: "Home" })).toBeTruthy();
    expect(screen.getByText("46%")).toBeTruthy();
    expect(screen.getByTestId("continua-link")).toHaveAttribute(
      "href",
      "/writing/2"
    );
    expect(screen.getByText("Ricerca")).toBeTruthy();
    expect(screen.getByText("Scrittura")).toBeTruthy();
    expect(screen.getByText("Revisione")).toBeTruthy();
    expect(screen.getByText("Importa documento")).toBeTruthy();
    expect(screen.getByText("Cap. 2")).toBeTruthy();
  });

  it("shows empty activity invitation", () => {
    render(
      <HomeView
        progressPct={0}
        continueTarget={{ href: "/writing", label: "Inizia" }}
        activity={[]}
      />
    );
    expect(screen.getByText(/Nessuna attività recente/i)).toBeTruthy();
  });

  it("Continua link restores persisted session state", async () => {
    localStorage.setItem(
      SESSION_STATE_STORAGE_KEY,
      JSON.stringify({
        chapterId: "3",
        chapterTitle: "Cap. 3 — Metodologia",
        section: "3.2",
        panel: "ai",
        updatedAt: new Date().toISOString(),
      })
    );

    render(
      <HomeView
        progressPct={40}
        continueTarget={{ href: "/writing/2", label: "Cap. 2" }}
        activity={[]}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId("continua-link")).toHaveAttribute(
        "href",
        "/writing/3?section=3.2&panel=ai#section-3-2"
      );
    });
  });

  it("shows pending proposal badge when queue non-empty", async () => {
    localStorage.setItem(
      PROPOSALS_STORAGE_KEY,
      JSON.stringify([{ id: "p1", title: "Test" }])
    );

    render(
      <HomeView
        progressPct={40}
        continueTarget={{ href: "/writing", label: "Scrittura" }}
        activity={[]}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId("home-pending-badge")).toHaveTextContent("1");
    });
  });

  it("renders PX-2 activity feed card types", () => {
    render(
      <HomeView
        progressPct={50}
        continueTarget={{ href: "/writing", label: "Scrittura" }}
        activityFeed={[
          {
            kind: "proposal_update",
            title: "Glossario STIGMATA",
            subtitle: "Definizione operativa del termine",
            meta: "1 ora fa",
          },
          {
            kind: "binding_decision",
            title: "CORPUS-02",
            subtitle: "Attenzione: decisione vincolante",
          },
        ]}
      />
    );

    expect(screen.getByText("Aggiornamento proposto")).toBeTruthy();
    expect(screen.getByText("Decisione vincolante")).toBeTruthy();
    expect(screen.getByText("Glossario STIGMATA")).toBeTruthy();
  });
});
