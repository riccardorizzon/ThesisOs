import { test } from "@playwright/test";

/**
 * Visual regression placeholders for PX-2+.
 * PX-1 qualification uses structural smoke only; pixel diffs deferred.
 */
test.describe("PX1 visual regression stubs @ui", () => {
  test.skip("Home screenshot baseline — deferred to PX-2", async () => {
    // Intentionally skipped: no baseline committed in PX-1.
  });

  test.skip("Writing three-panel layout screenshot — deferred to PX-2", async () => {
    // Intentionally skipped: responsive breakpoints need stable design tokens first.
  });
});
