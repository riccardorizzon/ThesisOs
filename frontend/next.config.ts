import type { NextConfig } from "next";
import { LEGACY_REDIRECTS, toNextRedirects } from "./lib/routes";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return toNextRedirects(LEGACY_REDIRECTS);
  },
};

export default nextConfig;
