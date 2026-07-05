/**
 * Product + legacy route registry — ADR-0036
 * Layer: Business (Product Plane)
 *
 * Used by tests; next.config.mjs mirrors legacyRedirects.
 */

export type ProductModule =
  | "home"
  | "research"
  | "writing"
  | "sources"
  | "knowledge"
  | "review"
  | "ai"
  | "settings";

export type ProductRoute = {
  path: string;
  module: ProductModule;
  milestone: string;
  description: string;
};

/** Spec §4 — PX-1 stub routes */
export const PRODUCT_ROUTES: ProductRoute[] = [
  { path: "/", module: "home", milestone: "PX-1", description: "Home" },
  {
    path: "/research",
    module: "research",
    milestone: "PX-5",
    description: "Research graph",
  },
  {
    path: "/writing",
    module: "writing",
    milestone: "PX-2",
    description: "Three-panel editor",
  },
  {
    path: "/sources",
    module: "sources",
    milestone: "PX-3",
    description: "Source library",
  },
  {
    path: "/knowledge",
    module: "knowledge",
    milestone: "PX-4",
    description: "Concept ontology",
  },
  {
    path: "/review",
    module: "review",
    milestone: "PX-1",
    description: "Revision workflow",
  },
  {
    path: "/ai",
    module: "ai",
    milestone: "PX-2",
    description: "AI power mode",
  },
  {
    path: "/settings",
    module: "settings",
    milestone: "PX-1",
    description: "Project settings",
  },
];

export type LegacyRedirect = {
  source: string;
  destination: string;
  permanent: boolean;
  adr: string;
};

/**
 * Legacy route disposition — ADR-0036
 * `/documents/*` → `/sources/*` (PX3-EWO-001)
 */
export const LEGACY_REDIRECTS: LegacyRedirect[] = [
  {
    source: "/chat",
    destination: "/ai",
    permanent: false,
    adr: "ADR-0036 — chat deprecated as primary home",
  },
  {
    source: "/library",
    destination: "/sources",
    permanent: false,
    adr: "ADR-0036 — library absorbed into Sources",
  },
  {
    source: "/workspace",
    destination: "/writing",
    permanent: false,
    adr: "ADR-0036 — workspace absorbed into Writing",
  },
  {
    source: "/outline",
    destination: "/writing",
    permanent: false,
    adr: "ADR-0036 — outline becomes Writing left panel",
  },
    {
        source: "/memory",
        destination: "/knowledge",
        permanent: false,
        adr: "ADR-0036 — memory admin split; primary → Knowledge",
    },
    {
        source: "/documents",
        destination: "/sources",
        permanent: false,
        adr: "ADR-0036 — documents absorbed into Sources (PX-3)",
    },
    {
        source: "/documents/:path*",
        destination: "/sources/:path*",
        permanent: false,
        adr: "ADR-0036 — documents/* → sources/* (PX-3)",
    },
];

/** Next.js redirect shape */
export function toNextRedirects(
  entries: LegacyRedirect[]
): { source: string; destination: string; permanent: boolean }[] {
  return entries.map(({ source, destination, permanent }) => ({
    source,
    destination,
    permanent,
  }));
}
