import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  API_PROXY_EXACT_PATHS,
  API_PROXY_PREFIXES,
  SSE_ROUTE_HANDLER_PATHS,
} from "@/lib/apiProxyPaths";
import nextConfig from "../next.config";

describe("API_PROXY_PREFIXES", () => {
  it("proxies proposals through the same ingress path the UI uses", () => {
    expect(API_PROXY_PREFIXES).toContain("proposals");
  });

  it("keeps chapters and projects on the public proxy allowlist", () => {
    expect(API_PROXY_PREFIXES).toContain("chapters");
    expect(API_PROXY_PREFIXES).toContain("projects");
  });

  it("does not treat writing/actions as a prefix (exact path only)", () => {
    expect(API_PROXY_PREFIXES).not.toContain("writing/actions");
    expect(API_PROXY_EXACT_PATHS).toContain("writing/actions");
  });

  it("lists SSE paths that use Route Handlers instead of rewrite buffering", () => {
    expect(SSE_ROUTE_HANDLER_PATHS).toEqual(
      expect.arrayContaining(["writing/actions", "chat"])
    );
  });

  it("keeps docker nginx SSE unbuffered for /api/", () => {
    const nginxPath = resolve(__dirname, "../../infra/docker/nginx.conf");
    if (!existsSync(nginxPath)) return;
    const nginx = readFileSync(nginxPath, "utf8");
    expect(nginx).toMatch(/location \^~ \/api\//);
    expect(nginx).toMatch(/proxy_buffering off;/);
    expect(nginx).toMatch(/proxy_set_header Accept-Encoding ""/);
    expect(nginx).toMatch(/writing\/actions/);
  });

  it("keeps nginx public ingress in sync for proposals when repo infra is present", () => {
    // Frontend Docker image only copies frontend/; skip there. Host/CI checkout has infra/.
    const nginxPath = resolve(__dirname, "../../infra/dev-vm/nginx-beta-public.conf");
    if (!existsSync(nginxPath)) {
      expect(API_PROXY_PREFIXES).toContain("proposals");
      return;
    }
    const nginx = readFileSync(nginxPath, "utf8");
    expect(nginx).toMatch(/\|proposals\|/);
  });

  it("namespaces browser API rewrites under /api and strips the prefix upstream", async () => {
    const result = await nextConfig.rewrites?.();
    expect(Array.isArray(result)).toBe(true);
    const rewrites = result as { source: string; destination: string }[];

    const documents = rewrites.find(
      (rewrite) => rewrite.source === "/api/documents/:path*"
    );

    // SSE paths use Route Handlers — must not appear as rewrites.
    expect(rewrites.some((rewrite) => rewrite.source === "/api/chat")).toBe(
      false
    );
    expect(
      rewrites.some((rewrite) => rewrite.source === "/api/writing/actions")
    ).toBe(false);
    expect(documents?.destination).toMatch(/\/documents\/:path\*$/);
    expect(rewrites.some((rewrite) => rewrite.source === "/chat")).toBe(false);
  });

  it("proxies /api through nginx before legacy UI routes", () => {
    const nginxPath = resolve(__dirname, "../../infra/dev-vm/nginx-beta-public.conf");
    if (!existsSync(nginxPath)) return;
    const nginx = readFileSync(nginxPath, "utf8");

    expect(nginx).toMatch(/location \^~ \/api\//);
    // Trailing slash on proxy_pass strips /api/ prefix (preferred over rewrite+break).
    expect(nginx).toMatch(/proxy_pass http:\/\/127\.0\.0\.1:8000\/;/);
    expect(nginx).toMatch(/chunked_transfer_encoding on;/);
  });
});

