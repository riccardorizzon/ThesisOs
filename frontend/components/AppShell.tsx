"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Breadcrumbs, ProjectSwitcher } from "@/components/navigation";
import { PRIMARY_NAV, isNavActive } from "@/lib/nav";
import { cn } from "@/lib/cn";

type AppShellProps = {
  children: React.ReactNode;
  /** Optional right panel slot — future AI action panel (ADR-0039) */
  rightPanel?: React.ReactNode;
};

const navLinkClass = (active: boolean) =>
  cn(
    "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
    active
      ? "bg-surface text-ink shadow-sm ring-1 ring-border"
      : "text-ink-muted hover:bg-surface-muted hover:text-ink"
  );

/**
 * Product AppShell — ADR-0036 sidebar + main + optional right panel.
 * Layer: Business (Product Plane)
 */
export function AppShell({ children, rightPanel }: AppShellProps) {
  const pathname = usePathname();
  const primaryRoutes = PRIMARY_NAV.filter((r) => r.group === "primary");
  const settingsRoutes = PRIMARY_NAV.filter((r) => r.group === "settings");

  return (
    <div className="flex min-h-screen bg-bg text-ink">
      <nav
        aria-label="Primary"
        className="flex w-sidebar shrink-0 flex-col border-r border-border bg-surface-muted"
      >
        <div className="space-y-3 border-b border-border px-4 py-4">
          <span className="text-lg font-semibold tracking-tight text-ink">
            ThesisOS
          </span>
          <ProjectSwitcher />
        </div>
        <ul className="flex-1 space-y-0.5 px-2 py-3">
          {primaryRoutes.map((route) => {
            const active = isNavActive(pathname, route.href);
            return (
              <li key={route.href}>
                <Link
                  href={route.href}
                  aria-current={active ? "page" : undefined}
                  className={navLinkClass(active)}
                >
                  {route.label}
                </Link>
              </li>
            );
          })}
        </ul>
        <div className="border-t border-border px-2 py-3">
          <ul>
            {settingsRoutes.map((route) => {
              const active = isNavActive(pathname, route.href);
              return (
                <li key={route.href}>
                  <Link
                    href={route.href}
                    aria-current={active ? "page" : undefined}
                    className={navLinkClass(active)}
                  >
                    {route.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>

      <div className="flex min-w-0 flex-1">
        <main className="min-w-0 flex-1 overflow-auto">
          <div className="border-b border-border bg-surface px-6 py-3">
            <Breadcrumbs />
          </div>
          <div className="p-6">{children}</div>
        </main>
        {rightPanel != null && (
          <aside
            aria-label="Panel"
            className="w-panel shrink-0 border-l border-border bg-surface-muted"
          >
            {rightPanel}
          </aside>
        )}
      </div>
    </div>
  );
}
