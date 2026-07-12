import type { NextConfig } from "next";
import { LEGACY_REDIRECTS, toNextRedirects } from "./lib/routes";
import { API_PROXY_EXACT_PATHS, API_PROXY_PREFIXES } from "./lib/apiProxyPaths";

const apiUpstream =
  process.env.INTERNAL_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return toNextRedirects(LEGACY_REDIRECTS);
  },
  async rewrites() {
    const prefixRewrites = API_PROXY_PREFIXES.flatMap((prefix) => [
      { source: `/${prefix}`, destination: `${apiUpstream}/${prefix}` },
      { source: `/${prefix}/:path*`, destination: `${apiUpstream}/${prefix}/:path*` },
    ]);
    const exactRewrites = API_PROXY_EXACT_PATHS.map((path) => ({
      source: `/${path}`,
      destination: `${apiUpstream}/${path}`,
    }));
    return [...prefixRewrites, ...exactRewrites];
  },
};

export default nextConfig;
