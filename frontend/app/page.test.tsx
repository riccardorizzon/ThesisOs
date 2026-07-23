import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/headers", () => ({
  cookies: async () => ({ toString: () => "" }),
}));
vi.mock("@/components/AiChatView", () => ({
  AiChatView: () => <div data-testid="ai-chat-view" />,
}));
vi.mock("@/components/HomeView", () => ({
  HomeView: () => <div data-testid="dashboard-home-view" />,
}));
vi.mock("@/lib/chapterClient", () => ({
  chapterClient: { list: vi.fn().mockResolvedValue([]) },
}));
vi.mock("@/lib/projectContext", () => ({
  DEFAULT_PROJECT_ID: "default-project",
}));
vi.mock("@/lib/projectPrefs", () => ({
  readActiveProjectIdCookie: () => null,
}));
vi.mock("@/lib/progress", () => ({
  computeProgressPct: () => 0,
  findContinueTarget: () => null,
}));
vi.mock("@/lib/workspacePrefs", () => ({
  chapterScopeForMode: () => "all",
  readWorkspaceModeCookie: () => "owned",
}));

import Home from "./page";

describe("latest home route", () => {
  it("opens directly on the chat-first workspace", async () => {
    render(await Home());

    expect(screen.getByTestId("ai-chat-view")).toBeInTheDocument();
    expect(screen.queryByTestId("dashboard-home-view")).not.toBeInTheDocument();
  });
});
