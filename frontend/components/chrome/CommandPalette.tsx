"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/cn";
import { ApiDegradedBanner } from "@/components/ui/ApiDegradedBanner";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import { getActiveProjectId } from "@/lib/projectPrefs";
import { PRIMARY_NAV } from "@/lib/nav";
import { dispatchOpenReview } from "@/components/review/reviewIntegration";
import { OPEN_COMMAND_PALETTE_EVENT } from "@/hooks/useKeyboardShortcuts";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export const TOGGLE_OUTLINE_EVENT = "thesisos:toggle-outline";
export const TOGGLE_RIGHT_RAIL_EVENT = "thesisos:toggle-right-rail";
export const FORCE_SAVE_EVENT = "thesisos:force-save";
export const FIND_IN_CHAPTER_EVENT = "thesisos:find-in-chapter";
export const APPLY_AI_SUGGESTION_EVENT = "thesisos:apply-ai-suggestion";
export const OUTLINE_PREV_SECTION_EVENT = "thesisos:outline-prev-section";
export const OUTLINE_NEXT_SECTION_EVENT = "thesisos:outline-next-section";
export const CITE_SOURCE_EVENT = "thesisos:insert-citation";

export type CommandAction = {
  id: string;
  group: string;
  label: string;
  shortcut?: string;
  keywords?: string[];
  run: () => void;
};

export type CommandPaletteState = {
  open: boolean;
  openPalette: () => void;
  closePalette: () => void;
  togglePalette: () => void;
};

function dispatchChromeEvent(name: string): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(name));
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      aria-hidden
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3-3" />
    </svg>
  );
}

export function useCommandPalette(): CommandPaletteState {
  const [open, setOpen] = useState(false);

  const openPalette = useCallback(() => setOpen(true), []);
  const closePalette = useCallback(() => setOpen(false), []);
  const togglePalette = useCallback(() => setOpen((v) => !v), []);

  useEffect(() => {
    const onOpen = () => setOpen(true);
    window.addEventListener(OPEN_COMMAND_PALETTE_EVENT, onOpen);
    return () => window.removeEventListener(OPEN_COMMAND_PALETTE_EVENT, onOpen);
  }, []);

  return { open, openPalette, closePalette, togglePalette };
}

export type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
};

/**
 * Global command palette — ⌘K / ⌘⇧P discoverability (PX2-EWO-008).
 * Layer: Business (Product Plane)
 */
export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const reducedMotion = useReducedMotion();
  const [query, setQuery] = useState("");
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [chaptersLoadError, setChaptersLoadError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setActiveIndex(0);
    setChaptersLoadError(null);
    chapterClient
      .list({ project_id: getActiveProjectId() })
      .then((list) => {
        setChapters(list);
        setChaptersLoadError(null);
      })
      .catch((err) => {
        setChapters([]);
        setChaptersLoadError(
          err instanceof Error ? err.message : "Impossibile caricare i capitoli."
        );
      });
    const frame = requestAnimationFrame(() => inputRef.current?.focus());
    return () => cancelAnimationFrame(frame);
  }, [open]);

  const baseActions = useMemo<CommandAction[]>(() => {
    const navRoutes = [
      ...PRIMARY_NAV.filter((r) => r.group === "primary"),
      { href: "/review", label: "Review", group: "primary" as const },
    ];

    const navigate = (href: string): CommandAction => ({
      id: `nav-${href}`,
      group: "Vai a…",
      label: `Vai a ${navRoutes.find((r) => r.href === href)?.label ?? href}`,
      keywords: [href],
      run: () => router.push(href),
    });

    return [
      navigate("/"),
      navigate("/writing"),
      navigate("/sources"),
      navigate("/review"),
      navigate("/research"),
      navigate("/knowledge"),
      {
        id: "toggle-outline",
        group: "Azioni",
        label: "Mostra/nascondi outline",
        shortcut: "⌘\\",
        run: () => dispatchChromeEvent(TOGGLE_OUTLINE_EVENT),
      },
      {
        id: "toggle-rail",
        group: "Azioni",
        label: "Mostra/nascondi pannello laterale",
        shortcut: "⌘⇧\\",
        run: () => dispatchChromeEvent(TOGGLE_RIGHT_RAIL_EVENT),
      },
      {
        id: "rail-ai",
        group: "Azioni",
        label: "Scheda AI",
        shortcut: "⌘1",
        run: () => dispatchChromeEvent("thesisos:rail-tab-1"),
      },
      {
        id: "rail-contesto",
        group: "Azioni",
        label: "Scheda Contesto",
        shortcut: "⌘2",
        run: () => dispatchChromeEvent("thesisos:rail-tab-2"),
      },
      {
        id: "rail-fonte",
        group: "Azioni",
        label: "Scheda Fonte",
        shortcut: "⌘3",
        run: () => dispatchChromeEvent("thesisos:rail-tab-3"),
      },
      {
        id: "rail-revisione",
        group: "Azioni",
        label: "Scheda Revisione",
        shortcut: "⌘4",
        run: () => dispatchChromeEvent("thesisos:rail-tab-4"),
      },
      {
        id: "force-save",
        group: "Azioni",
        label: "Salva capitolo",
        shortcut: "⌘S",
        run: () => dispatchChromeEvent(FORCE_SAVE_EVENT),
      },
      {
        id: "cite",
        group: "Azioni",
        label: "Cita fonte",
        shortcut: "⌘⇧C",
        run: () => dispatchChromeEvent(CITE_SOURCE_EVENT),
      },
      {
        id: "find",
        group: "Azioni",
        label: "Cerca nel capitolo",
        shortcut: "⌘⇧F",
        run: () => dispatchChromeEvent(FIND_IN_CHAPTER_EVENT),
      },
      {
        id: "review",
        group: "Azioni",
        label: "Avvia revisione capitolo",
        shortcut: "⌘⇧R",
        run: () => dispatchOpenReview(),
      },
      {
        id: "apply-ai",
        group: "Azioni",
        label: "Applica suggerimento AI",
        shortcut: "⌘Enter",
        run: () => dispatchChromeEvent(APPLY_AI_SUGGESTION_EVENT),
      },
      {
        id: "outline-up",
        group: "Azioni",
        label: "Sezione precedente",
        shortcut: "⌘↑",
        run: () => dispatchChromeEvent(OUTLINE_PREV_SECTION_EVENT),
      },
      {
        id: "outline-down",
        group: "Azioni",
        label: "Sezione successiva",
        shortcut: "⌘↓",
        run: () => dispatchChromeEvent(OUTLINE_NEXT_SECTION_EVENT),
      },
      {
        id: "goto-writing",
        group: "Scorciatoie",
        label: "Vai a Scrittura",
        shortcut: "G W",
        run: () => router.push("/writing"),
      },
      {
        id: "goto-sources",
        group: "Scorciatoie",
        label: "Vai a Fonti",
        shortcut: "G S",
        run: () => router.push("/sources"),
      },
      {
        id: "goto-home",
        group: "Scorciatoie",
        label: "Vai a Home",
        shortcut: "G H",
        run: () => router.push("/"),
      },
    ];
  }, [router]);

  const chapterActions = useMemo<CommandAction[]>(
    () =>
      chapters.map((chapter) => ({
        id: `chapter-${chapter.id}`,
        group: "Capitoli",
        label: chapter.title,
        keywords: [chapter.id, chapter.status],
        run: () => router.push(`/writing/${chapter.id}`),
      })),
    [chapters, router]
  );

  const allActions = useMemo(
    () => [...baseActions, ...chapterActions],
    [baseActions, chapterActions]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return allActions;
    return allActions.filter((action) => {
      const haystack = [
        action.label,
        action.group,
        action.shortcut ?? "",
        ...(action.keywords ?? []),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [allActions, query]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  const execute = useCallback(
    (action: CommandAction) => {
      action.run();
      onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (filtered.length === 0) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex((i) => (i + 1) % filtered.length);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex((i) => (i - 1 + filtered.length) % filtered.length);
      } else if (event.key === "Enter") {
        event.preventDefault();
        const action = filtered[activeIndex];
        if (action) execute(action);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, filtered, activeIndex, execute, onClose]);

  if (!open) return null;

  const grouped = filtered.reduce<Record<string, CommandAction[]>>((acc, action) => {
    acc[action.group] ??= [];
    acc[action.group].push(action);
    return acc;
  }, {});

  let rowIndex = 0;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-start justify-center bg-ink/20 px-4 pt-[12vh]"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Palette comandi"
        className={cn(
          "w-full max-w-lg rounded-lg border border-border bg-surface shadow-md",
          !reducedMotion && "opacity-100"
        )}
      >
        <div className="flex items-center gap-2 border-b border-border px-3 py-2.5">
          <SearchIcon className="h-4 w-4 text-ink-subtle" />
          <span className="text-xs font-medium text-ink-subtle">⌘K</span>
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Cerca azioni, capitoli, scorciatoie…"
            aria-label="Cerca comandi"
            className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-subtle"
            data-testid="command-palette-input"
          />
        </div>

        {chaptersLoadError ? (
          <ApiDegradedBanner
            message={chaptersLoadError}
            className="mx-3 mt-2"
            testId="command-palette-chapters-degraded"
          />
        ) : null}

        <div
          className="max-h-80 overflow-y-auto py-1"
          role="listbox"
          aria-label="Risultati comandi"
        >
          {filtered.length === 0 ? (
            <p className="px-4 py-6 text-center text-sm text-ink-muted">
              Nessun risultato
            </p>
          ) : (
            Object.entries(grouped).map(([group, actions]) => (
              <div key={group}>
                <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-ink-subtle">
                  {group}
                </p>
                <ul>
                  {actions.map((action) => {
                    const index = rowIndex;
                    rowIndex += 1;
                    const selected = index === activeIndex;
                    return (
                      <li key={action.id}>
                        <button
                          type="button"
                          role="option"
                          aria-selected={selected}
                          className={cn(
                            "flex w-full items-center gap-3 px-3 py-2 text-left text-sm",
                            "transition-colors duration-200",
                            selected
                              ? "bg-accent-subtle text-ink"
                              : "text-ink hover:bg-surface-muted"
                          )}
                          onMouseEnter={() => setActiveIndex(index)}
                          onClick={() => execute(action)}
                          data-testid={`command-action-${action.id}`}
                        >
                          <span className="flex-1">{action.label}</span>
                          {action.shortcut ? (
                            <kbd className="shrink-0 rounded border border-border bg-surface-muted px-1.5 py-0.5 text-xs text-ink-subtle">
                              {action.shortcut}
                            </kbd>
                          ) : null}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
