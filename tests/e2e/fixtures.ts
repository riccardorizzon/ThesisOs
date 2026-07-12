import { test as base, expect } from "@playwright/test";

/**
 * RC-4C Welcome gate — e2e/CI skip the first-run welcome without disabling it in production.
 */
export const test = base.extend({
  context: async ({ context }, use) => {
    await context.addInitScript(() => {
      localStorage.setItem("thesisos:welcome-complete", "1");
      localStorage.setItem("thesisos:workspace-mode", "personal");
      localStorage.setItem(
        "thesisos-onboarding-m7",
        JSON.stringify({ dismissed: true, completedSteps: [1, 2, 3, 4, 5] })
      );
      document.cookie = "thesisos-welcome-complete=1; path=/; samesite=lax";
      document.cookie = "thesisos-workspace-mode=personal; path=/; samesite=lax";
    });
    await use(context);
  },
});

export { expect };
