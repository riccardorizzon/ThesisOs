import { beforeEach, describe, expect, it } from "vitest";

import { clearProjectBrowserState } from "@/lib/projectPrefs";

beforeEach(() => {
  localStorage.clear();
});

describe("clearProjectBrowserState", () => {
  it("removes only keys namespaced to the deleted project", () => {
    localStorage.setItem("thesisos:thesis-002:session-state", "delete");
    localStorage.setItem("thesisos:thesis-002:project-prefs", "delete");
    localStorage.setItem("thesisos:thesis-agent:session-state", "keep");
    localStorage.setItem("thesisos:last-personal-project-id", "thesis-002");
    localStorage.setItem("unrelated", "keep");

    clearProjectBrowserState("thesis-002");

    expect(localStorage.getItem("thesisos:thesis-002:session-state")).toBeNull();
    expect(localStorage.getItem("thesisos:thesis-002:project-prefs")).toBeNull();
    expect(localStorage.getItem("thesisos:thesis-agent:session-state")).toBe("keep");
    expect(localStorage.getItem("thesisos:last-personal-project-id")).toBe(
      "thesis-agent"
    );
    expect(localStorage.getItem("unrelated")).toBe("keep");
  });
});
