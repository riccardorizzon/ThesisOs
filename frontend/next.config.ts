import type { NextConfig } from "next";
import { LEGACY_REDIRECTS, toNextRedirects } from "./lib/routes";
import {
  API_PROXY_EXACT_PATHS,
  API_PROXY_PREFIXES,
  SSE_ROUTE_HANDLER_PATHS,
} from "./lib/apiProxyPaths";

const apiUpstream =
  process.env.INTERNAL_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

const sseHandlerSet = new Set<string>(SSE_ROUTE_HANDLER_PATHS);

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return toNextRedirects(LEGACY_REDIRECTS);
  },
  async rewrites() {
    // SSE paths use App Router Route Handlers (proxySsePost) — rewrites buffer/close streams.
    const prefixRewrites = API_PROXY_PREFIXES.filter(
      (prefix) => !sseHandlerSet.has(prefix)
    ).flatMap((prefix) => [
      { source: `/api/${prefix}`, destination: `${apiUpstream}/${prefix}` },
      {
        source: `/api/${prefix}/:path*`,
        destination: `${apiUpstream}/${prefix}/:path*`,
      },
    ]);
    const exactRewrites = API_PROXY_EXACT_PATHS.filter(
      (path) => !sseHandlerSet.has(path)
    ).map((path) => ({
      source: `/api/${path}`,
      destination: `${apiUpstream}/${path}`,
    }));
    return [...prefixRewrites, ...exactRewrites];
  },
};

export default nextConfig;
