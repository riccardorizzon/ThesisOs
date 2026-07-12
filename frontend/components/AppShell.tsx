"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Breadcrumbs, ProjectSwitcher } from "@/components/navigation";
import { SessionChip } from "@/components/chrome/SessionChip";
import {
  CommandPalette,
  useCommandPalette,
} from "@/components/chrome/CommandPalette";
import { OfflineBanner } from "@/components/chrome/OfflineBanner";
import { CoachMarkProvider } from "@/components/onboarding/CoachMark";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import { listPendingProposals } from "@/lib/proposalQueue";
import { PRIMARY_NAV, isNavActive } from "@/lib/nav";
import { chapterScopeForMode, getWorkspaceMode } from "@/lib/workspacePrefs";
import { cn } from "@/lib/cn";

type AppShellProps = {
  children: React.ReactNode;
  /** Optional right panel slot — future AI action panel (ADR-0039) */
  rightPanel?: React.ReactNode;
};

const navLinkClass = (active: boolean) =>
  cn(
    "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
    active
      ? "bg-surface text-ink shadow-sm ring-1 ring-border"
      : "text-ink-muted hover:bg-surface-muted hover:text-ink"
  );

function writingStatusDot(chapters: Chapter[]): "draft" | "in_review" | null {
  if (chapters.length === 0) return null;
  const hasReview = chapters.some(
    (chapter) => chapter.status === "review" || chapter.status === "approved"
  );
  return hasReview ? "in_review" : "draft";
}

/**
 * Product AppShell — ADR-0036 sidebar + main + optional right panel.
 * Layer: Business (Product Plane)
 */
export function AppShell({ children, rightPanel }: AppShellProps) {
  const pathname = usePathname();
  const primaryRoutes = PRIMARY_NAV.filter((r) => r.group === "primary");
  const settingsRoutes = PRIMARY_NAV.filter((r) => r.group === "settings");
  const { open, openPalette, closePalette } = useCommandPalette();
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [pendingReviewCount, setPendingReviewCount] = useState(0);

  const refreshBadges = useCallback(() => {
    const scope = chapterScopeForMode(getWorkspaceMode());
    chapterClient
      .list({ scope })
      .then(setChapters)
      .catch(() => setChapters([]));
    setPendingReviewCount(listPendingProposals().length);
  }, []);

  useEffect(() => {
    refreshBadges();
    const onBundle = () => refreshBadges();
    window.addEventListener("thesisos:proposal-bundle-resolved", onBundle);
    return () =>
      window.removeEventListener("thesisos:proposal-bundle-resolved", onBundle);
  }, [refreshBadges]);

  useKeyboardShortcuts({ onOpenCommandPalette: openPalette });

  const writingDot = writingStatusDot(chapters);
  const homeProposalCount = pendingReviewCount;

  return (
    <div className="flex min-h-screen bg-bg text-ink">
      <OfflineBanner />
      <CommandPalette open={open} onClose={closePalette} />
      <CoachMarkProvider pathname={pathname} />

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
            const showHomeBadge =
              route.href === "/" && homeProposalCount > 0;
            const showWritingDot = route.href === "/writing" && writingDot != null;

            return (
              <li key={route.href}>
                <Link
                  href={route.href}
                  aria-current={active ? "page" : undefined}
                  className={navLinkClass(active)}
                >
                  <span className="flex-1">{route.label}</span>
                  {showHomeBadge ? (
                    <>
                      <span
                        className="inline-flex min-w-[1.25rem] items-center justify-center rounded-full bg-accent px-1.5 py-0.5 text-xs font-medium text-white"
                        aria-hidden="true"
                        data-testid="nav-badge-home"
                      >
                        {homeProposalCount}
                      </span>
                      <span className="sr-only">
                        {homeProposalCount} proposte in sospeso
                      </span>
                    </>
                  ) : null}
                  {showWritingDot ? (
                    <span
                      className={cn(
                        "h-2 w-2 shrink-0 rounded-full",
                        writingDot === "in_review" ? "bg-warning" : "bg-ink-subtle"
                      )}
                      aria-label={
                        writingDot === "in_review"
                          ? "Capitolo in revisione"
                          : "Capitolo in bozza"
                      }
                      data-testid="nav-badge-writing"
                    />
                  ) : null}
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
          {pendingReviewCount > 0 ? (
            <p
              className="mt-2 px-3 text-xs text-ink-subtle"
              data-testid="nav-review-pending"
            >
              Revisione: {pendingReviewCount} in sospeso
            </p>
          ) : null}
        </div>
      </nav>

      <div className="flex min-w-0 flex-1">
        <main className="min-w-0 flex-1 overflow-auto">
          <div className="flex items-center justify-between gap-4 border-b border-border bg-surface px-6 py-3">
            <Breadcrumbs />
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={openPalette}
                className={cn(
                  "hidden items-center gap-1.5 rounded-md px-2.5 py-1.5 lg:inline-flex",
                  "text-xs font-medium text-ink-muted transition-colors duration-200",
                  "hover:bg-surface-muted hover:text-ink",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent"
                )}
                aria-label="Apri palette comandi"
                data-testid="command-palette-trigger"
              >
                <svg
                  className="h-3.5 w-3.5"
                  aria-hidden
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <circle cx="11" cy="11" r="7" />
                  <path d="M20 20l-3-3" />
                </svg>
                <span>⌘K</span>
              </button>
              <SessionChip />
            </div>
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
