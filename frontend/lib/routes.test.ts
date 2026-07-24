import { describe, expect, it } from "vitest";
import { LEGACY_REDIRECTS, PRODUCT_ROUTES, toNextRedirects } from "./routes";

describe("PRODUCT_ROUTES", () => {
  it("includes Spec §4 module paths", () => {
    const paths = PRODUCT_ROUTES.map((r) => r.path);
    expect(paths).toContain("/");
    expect(paths).toContain("/research");
    expect(paths).toContain("/research/canvas");
    expect(paths).not.toContain("/research/guided");
    expect(paths).toContain("/writing");
    expect(paths).toContain("/sources");
    expect(paths).toContain("/knowledge");
    expect(paths).toContain("/review");
    expect(paths).toContain("/ai");
    expect(paths).toContain("/settings");
  });

  it("registers /review as distinct from /ai per ADR-0039", () => {
    const review = PRODUCT_ROUTES.find((r) => r.path === "/review");
    const ai = PRODUCT_ROUTES.find((r) => r.path === "/ai");
    expect(review?.module).toBe("review");
    expect(ai?.module).toBe("ai");
    expect(review?.module).not.toBe(ai?.module);
  });
});

describe("LEGACY_REDIRECTS", () => {
  it("redirects /chat to /ai per ADR-0036", () => {
    const chat = LEGACY_REDIRECTS.find((r) => r.source === "/chat");
    expect(chat?.destination).toBe("/ai");
  });

  it("maps legacy modules to product routes", () => {
    expect(LEGACY_REDIRECTS.find((r) => r.source === "/library")?.destination).toBe(
      "/sources"
    );
    expect(LEGACY_REDIRECTS.find((r) => r.source === "/workspace")?.destination).toBe(
      "/writing"
    );
    expect(LEGACY_REDIRECTS.find((r) => r.source === "/outline")?.destination).toBe(
      "/writing"
    );
    expect(LEGACY_REDIRECTS.find((r) => r.source === "/memory")?.destination).toBe(
      "/knowledge?view=notes"
    );
    expect(
      LEGACY_REDIRECTS.find((r) => r.source === "/memory/:path*")?.destination
    ).toBe("/knowledge?view=notes");
  });

  it("redirects /documents to /sources per PX3-EWO-001", () => {
    expect(LEGACY_REDIRECTS.find((r) => r.source === "/documents")?.destination).toBe(
      "/sources"
    );
    expect(
      LEGACY_REDIRECTS.find((r) => r.source === "/documents/:path*")?.destination
    ).toBe("/sources/:path*");
  });

  it("produces valid Next.js redirect objects", () => {
    const next = toNextRedirects(LEGACY_REDIRECTS);
    expect(next.every((r) => r.source.startsWith("/"))).toBe(true);
    expect(next.every((r) => r.destination.startsWith("/"))).toBe(true);
  });
});
