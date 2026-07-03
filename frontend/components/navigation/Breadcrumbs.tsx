"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { buildBreadcrumbs, shouldShowBreadcrumbs } from "@/lib/nav";

/**
 * Route-aware breadcrumbs for module and nested dynamic routes.
 * Layer: Business (Product Plane)
 */
export function Breadcrumbs() {
  const pathname = usePathname() ?? "/";

  if (!shouldShowBreadcrumbs(pathname)) {
    return null;
  }

  const segments = buildBreadcrumbs(pathname);

  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1 text-sm text-ink-muted">
        {segments.map((segment, index) => {
          const isLast = index === segments.length - 1;
          return (
            <li key={`${segment.label}-${index}`} className="flex items-center gap-1">
              {index > 0 && (
                <span aria-hidden className="text-ink-subtle">
                  /
                </span>
              )}
              {segment.href != null && !isLast ? (
                <Link
                  href={segment.href}
                  className="font-medium text-accent underline-offset-2 hover:underline"
                >
                  {segment.label}
                </Link>
              ) : (
                <span
                  aria-current={isLast ? "page" : undefined}
                  className={isLast ? "font-medium text-ink" : undefined}
                >
                  {segment.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
