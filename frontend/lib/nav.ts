/**
 * Primary navigation — ADR-0036 Information Architecture
 * Layer: Business (Product Plane)
 */

export type NavRoute = {
  href: string;
  label: string;
  /** Primary module vs settings separator group */
  group: "primary" | "settings";
};

/** INV-IA-1: exactly six primary modules + Settings */
export const PRIMARY_NAV: NavRoute[] = [
  { href: "/", label: "Home", group: "primary" },
  { href: "/research", label: "Research", group: "primary" },
  { href: "/writing", label: "Writing", group: "primary" },
  { href: "/sources", label: "Sources", group: "primary" },
  { href: "/knowledge", label: "Knowledge", group: "primary" },
  { href: "/settings", label: "Settings", group: "settings" },
];

export function isNavActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export type BreadcrumbSegment = {
  label: string;
  href?: string;
};

const MODULE_LABEL_BY_ROOT = new Map(
  PRIMARY_NAV.filter((route) => route.href !== "/").map((route) => [
    route.href,
    route.label,
  ])
);

/** Humanize dynamic route segments (chapter ids, concept slugs, etc.). */
export function formatBreadcrumbLabel(segment: string): string {
  try {
    return decodeURIComponent(segment).replace(/-/g, " ");
  } catch {
    return segment;
  }
}

/**
 * Build route-aware breadcrumbs for module and nested dynamic routes.
 * Home (`/`) returns an empty trail — module chrome starts at module roots.
 */
export function buildBreadcrumbs(pathname: string): BreadcrumbSegment[] {
  const normalized = pathname.replace(/\/+$/, "") || "/";
  if (normalized === "/") return [];

  const segments = normalized.split("/").filter(Boolean);
  const rootPath = `/${segments[0]}`;
  const moduleLabel = MODULE_LABEL_BY_ROOT.get(rootPath);

  if (moduleLabel == null) {
    return segments.map((segment, index) => {
      const href = `/${segments.slice(0, index + 1).join("/")}`;
      return {
        label: formatBreadcrumbLabel(segment),
        href: index < segments.length - 1 ? href : undefined,
      };
    });
  }

  if (segments.length === 1) {
    return [{ label: moduleLabel }];
  }

  const crumbs: BreadcrumbSegment[] = [{ label: moduleLabel, href: rootPath }];
  let path = rootPath;
  for (let index = 1; index < segments.length; index += 1) {
    path += `/${segments[index]}`;
    crumbs.push({
      label: formatBreadcrumbLabel(segments[index]),
      href: index < segments.length - 1 ? path : undefined,
    });
  }
  return crumbs;
}

export function shouldShowBreadcrumbs(pathname: string): boolean {
  return buildBreadcrumbs(pathname).length > 0;
}
