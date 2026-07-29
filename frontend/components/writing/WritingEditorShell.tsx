"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/cn";
import {
  MarkdownEditor,
  countWords,
  parseMarkdownSections,
  saveStateLabel,
  type MarkdownEditorHandle,
  type SaveState,
} from "@/components/writing/MarkdownEditor";
import {
  ChapterApiError,
  chapterClient,
  type Chapter,
  type ChapterStatus,
} from "@/lib/chapterClient";
import { SourcePicker } from "@/components/sources/SourcePicker";
import { corpusClient } from "@/lib/corpusClient";
import { dispatchOpenFontePeek } from "@/components/writing/rightRailIntegration";
import { ExportMenu } from "@/components/writing/ExportMenu";
import { ChapterDeleteButton } from "@/components/writing/ChapterDeleteButton";
import { ChapterVersionsPanel } from "@/components/writing/ChapterVersionsPanel";
import { ManuscriptMarkdown } from "@/components/manuscript/ManuscriptMarkdown";
import { useWritingEditorChrome } from "@/lib/writingChromeIntegration";
import { persistChapterMetadata } from "@/lib/chapterMetadata";
import { CHAPTER_STATUS_LABELS } from "@/components/writing/writingTypes";

function sectionWordCount(content: string, sectionId: string): number {
  const sections = parseMarkdownSections(content);
  const idx = sections.findIndex((s) => s.id === sectionId);
  if (idx === -1) return 0;
  const lines = content.split("\n");
  const startLine = sections[idx].lineIndex + 1;
  const endLine = idx + 1 < sections.length ? sections[idx + 1].lineIndex : lines.length;
  return countWords(lines.slice(startLine, endLine).join("\n"));
}

export type WritingEditorShellProps = {
  chapterId?: string;
  chapter?: Chapter | null;
  activeSectionId?: string;
  readOnly?: boolean;
  onChapterUpdated?: (chapter: Chapter) => void;
  onChapterDeleted?: (chapterId: string) => void;
  onSectionsChange?: (sections: ReturnType<typeof parseMarkdownSections>) => void;
  className?: string;
};

function SaveIndicator({ state }: { state: SaveState }) {
  const label = saveStateLabel(state);
  if (!label) return null;

  const tone =
    state === "saved"
      ? "text-success"
      : state === "saving"
        ? "text-ink-muted"
        : "text-warning";

  return (
    <span
      className={cn("flex items-center gap-1.5 text-xs font-medium", tone)}
      data-testid="editor-save-indicator"
      data-state={state}
      aria-live="polite"
    >
      {state === "saving" && (
        <span
          className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden
        />
      )}
      {label}
    </span>
  );
}

function ConflictDialog({
  open,
  onReload,
  onOverwrite,
  onDismiss,
}: {
  open: boolean;
  onReload: () => void;
  onOverwrite: () => void;
  onDismiss: () => void;
}) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="conflict-dialog-title"
      data-testid="chapter-conflict-dialog"
    >
      <div className="w-full max-w-md rounded-lg border border-border bg-surface p-5 shadow-md">
        <h3 id="conflict-dialog-title" className="text-base font-semibold text-ink">
          Capitolo modificato altrove
        </h3>
        <p className="mt-2 text-sm text-ink-muted">
          Un&apos;altra scheda ha salvato modifiche a questo capitolo. Ricarica per
          vedere la versione più recente, oppure sovrascrivi con il contenuto di questa
          scheda.
        </p>
        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <button
            type="button"
            onClick={onDismiss}
            className="rounded-md border border-border px-3 py-1.5 text-sm text-ink-muted hover:bg-surface-muted"
          >
            Annulla
          </button>
          <button
            type="button"
            onClick={onReload}
            className="rounded-md border border-border px-3 py-1.5 text-sm font-medium text-ink hover:bg-surface-muted"
          >
            Ricarica
          </button>
          <button
            type="button"
            onClick={onOverwrite}
            className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-ink-inverse hover:bg-accent-muted"
          >
            Sovrascrivi con questa scheda
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Markdown editor shell — center panel with autosave (PX2-EWO-002).
 * Layer: Business (Product Plane)
 */
export function WritingEditorShell({
  chapterId,
  chapter: chapterProp,
  activeSectionId,
  readOnly = false,
  onChapterUpdated,
  onChapterDeleted,
  onSectionsChange,
  className,
}: WritingEditorShellProps) {
  const editorRef = useRef<MarkdownEditorHandle>(null);
  const [chapter, setChapter] = useState<Chapter | null>(chapterProp ?? null);
  const [content, setContent] = useState("");
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [loading, setLoading] = useState(false);
  const [conflictOpen, setConflictOpen] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [findOpen, setFindOpen] = useState(false);
  const [findQuery, setFindQuery] = useState("");
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");
  const [metadataBusy, setMetadataBusy] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [versionsOpen, setVersionsOpen] = useState(false);
  const skipTitleBlurRef = useRef(false);
  const versionRef = useRef(1);

  useEffect(() => {
    if (chapterProp) {
      setChapter(chapterProp);
      setContent(chapterProp.content_md ?? "");
      versionRef.current = chapterProp.version;
      setSaveState("saved");
    }
  }, [chapterProp]);

  useEffect(() => {
    if (chapterProp || !chapterId) return;

    let cancelled = false;
    setLoading(true);
    void chapterClient
      .get(chapterId)
      .then((ch) => {
        if (cancelled) return;
        setChapter(ch);
        setContent(ch.content_md ?? "");
        versionRef.current = ch.version;
        setSaveState("saved");
        onChapterUpdated?.(ch);
      })
      .catch(() => {
        if (!cancelled) {
          setChapter(null);
          setContent("");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [chapterId, chapterProp, onChapterUpdated]);

  useEffect(() => {
    onSectionsChange?.(parseMarkdownSections(content));
  }, [content, onSectionsChange]);

  const persistContent = useCallback(
    async (nextContent: string, forceVersion?: number) => {
      if (!chapter) throw new Error("No chapter loaded");
      const updated = await chapterClient.update(chapter.id, {
        content_md: nextContent,
        expected_version: forceVersion ?? versionRef.current,
      });
      versionRef.current = updated.version;
      setChapter(updated);
      onChapterUpdated?.(updated);
      return updated;
    },
    [chapter, onChapterUpdated]
  );

  const handleSave = useCallback(
    async (nextContent: string) => {
      if (!chapter || readOnly) return;
      try {
        await persistContent(nextContent);
        setSaveState("saved");
      } catch (err) {
        if (err instanceof ChapterApiError && err.status === 409) {
          setConflictOpen(true);
        }
        throw err;
      }
    },
    [chapter, persistContent, readOnly]
  );

  const handleReload = useCallback(async () => {
    if (!chapter) return;
    setConflictOpen(false);
    const fresh = await chapterClient.get(chapter.id);
    setChapter(fresh);
    setContent(fresh.content_md ?? "");
    versionRef.current = fresh.version;
    setSaveState("saved");
    onChapterUpdated?.(fresh);
  }, [chapter, onChapterUpdated]);

  const handleOverwrite = useCallback(async () => {
    if (!chapter) return;
    setConflictOpen(false);
    try {
      const fresh = await chapterClient.get(chapter.id);
      versionRef.current = fresh.version;
      await persistContent(content, fresh.version);
      setSaveState("saved");
    } catch (err) {
      if (err instanceof ChapterApiError && err.status === 409) {
        setConflictOpen(true);
      } else {
        setSaveState("error");
      }
    }
  }, [chapter, content, persistContent]);

  useEffect(() => {
    const interval = setInterval(() => {
      const state = editorRef.current?.getSaveState();
      if (state) setSaveState(state);
    }, 200);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || !event.shiftKey || event.key.toLowerCase() !== "c") return;
      event.preventDefault();
      setPickerOpen(true);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const handleForceSave = useCallback(() => {
    void editorRef.current?.flushSave();
  }, []);

  const handleFindInChapter = useCallback(() => {
    setFindOpen(true);
  }, []);

  const startTitleEdit = useCallback(() => {
    if (readOnly || !chapter) return;
    setTitleDraft(chapter.title);
    setEditingTitle(true);
  }, [chapter, readOnly]);

  const cancelTitleEdit = useCallback(() => {
    skipTitleBlurRef.current = true;
    setEditingTitle(false);
    setTitleDraft("");
  }, []);

  const saveTitle = useCallback(async () => {
    if (!chapter || readOnly || metadataBusy) return;
    const trimmed = titleDraft.trim();
    if (!trimmed || trimmed === chapter.title) {
      cancelTitleEdit();
      return;
    }
    setMetadataBusy(true);
    try {
      const updated = await persistChapterMetadata(
        { id: chapter.id, version: versionRef.current },
        { title: trimmed }
      );
      versionRef.current = updated.version;
      setChapter(updated);
      onChapterUpdated?.(updated);
      setEditingTitle(false);
      setTitleDraft("");
      setSaveState("saved");
    } catch (err) {
      if (err instanceof ChapterApiError && err.status === 409) {
        setConflictOpen(true);
      } else {
        setSaveState("error");
      }
    } finally {
      setMetadataBusy(false);
    }
  }, [cancelTitleEdit, chapter, metadataBusy, onChapterUpdated, readOnly, titleDraft]);

  const handleTitleBlur = useCallback(() => {
    if (skipTitleBlurRef.current) {
      skipTitleBlurRef.current = false;
      return;
    }
    void saveTitle();
  }, [saveTitle]);

  const togglePreview = useCallback(() => {
    if (!previewMode) {
      void editorRef.current?.flushSave();
    }
    setPreviewMode((value) => !value);
  }, [previewMode]);

  const saveStatus = useCallback(
    async (status: ChapterStatus) => {
      if (!chapter || readOnly || metadataBusy || status === chapter.status) return;
      setMetadataBusy(true);
      try {
        const updated = await persistChapterMetadata(
          { id: chapter.id, version: versionRef.current },
          { status }
        );
        versionRef.current = updated.version;
        setChapter(updated);
        onChapterUpdated?.(updated);
        setSaveState("saved");
      } catch (err) {
        if (err instanceof ChapterApiError && err.status === 409) {
          setConflictOpen(true);
        } else {
          setSaveState("error");
        }
      } finally {
        setMetadataBusy(false);
      }
    },
    [chapter, metadataBusy, onChapterUpdated, readOnly]
  );

  useWritingEditorChrome({
    onForceSave: handleForceSave,
    onFindInChapter: handleFindInChapter,
    onCiteSource: () => setPickerOpen(true),
  });

  useEffect(() => {
    if (!findOpen || !findQuery.trim() || !editorRef.current) return;
    editorRef.current.scrollToSection(
      parseMarkdownSections(content).find((section) =>
        section.label.toLowerCase().includes(findQuery.trim().toLowerCase())
      )?.id ?? findQuery.trim()
    );
  }, [findOpen, findQuery, content]);

  const title = chapter?.title ?? (chapterId ? `Capitolo ${chapterId}` : "Seleziona un capitolo");
  const sectionWords = activeSectionId
    ? sectionWordCount(content, activeSectionId)
    : 0;
  const chapterWords = chapter?.word_count ?? countWords(content);

  return (
    <section
      aria-label="Editor Markdown"
      className={cn("flex h-full flex-col", className)}
    >
      <header className="flex h-10 shrink-0 items-center justify-between border-b border-border px-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="min-w-0 flex items-center gap-2">
            {editingTitle ? (
              <input
                type="text"
                value={titleDraft}
                onChange={(event) => setTitleDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void saveTitle();
                  }
                  if (event.key === "Escape") {
                    event.preventDefault();
                    cancelTitleEdit();
                  }
                }}
                onBlur={handleTitleBlur}
                disabled={metadataBusy}
                autoFocus
                className="min-w-0 max-w-xs truncate rounded border border-border bg-surface px-2 py-0.5 text-sm font-semibold text-ink"
                data-testid="chapter-title-input"
                aria-label="Titolo capitolo"
              />
            ) : (
              <button
                type="button"
                onClick={startTitleEdit}
                disabled={readOnly || !chapter}
                className="min-w-0 truncate text-left text-sm font-semibold text-ink disabled:cursor-default disabled:opacity-70"
                data-testid="chapter-title-display"
                title={readOnly || !chapter ? undefined : "Rinomina capitolo"}
              >
                {title}
              </button>
            )}
            {chapter ? (
              <select
                value={chapter.status}
                onChange={(event) =>
                  void saveStatus(event.target.value as ChapterStatus)
                }
                disabled={readOnly || metadataBusy}
                className="shrink-0 rounded border border-border bg-surface px-1.5 py-0.5 text-xs text-ink-muted disabled:opacity-50"
                data-testid="chapter-status-select"
                aria-label="Stato capitolo"
              >
                {(Object.keys(CHAPTER_STATUS_LABELS) as ChapterStatus[]).map((status) => (
                  <option key={status} value={status}>
                    {CHAPTER_STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            ) : null}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPickerOpen(true)}
              disabled={readOnly || !chapter}
              className="hidden rounded px-2 py-1 text-xs text-ink-muted hover:text-ink disabled:opacity-50 sm:inline"
              title="Cita fonte (⌘⇧C)"
            >
              Cita
            </button>
            <button
              type="button"
              onClick={() => setFindOpen(true)}
              disabled={readOnly || !chapter}
              className="hidden rounded px-2 py-1 text-xs text-ink-muted hover:text-ink disabled:opacity-50 sm:inline"
              data-testid="find-in-chapter-trigger"
            >
              Find
            </button>
            <button
              type="button"
              onClick={togglePreview}
              disabled={!chapter}
              className={cn(
                "rounded px-2 py-1 text-xs hover:text-ink disabled:opacity-50",
                previewMode ? "font-medium text-accent" : "text-ink-muted"
              )}
              data-testid="writing-preview-toggle"
              aria-pressed={previewMode}
            >
              Preview
            </button>
            <button
              type="button"
              onClick={() => setVersionsOpen((value) => !value)}
              disabled={readOnly || !chapter}
              className={cn(
                "rounded px-2 py-1 text-xs hover:text-ink disabled:opacity-50",
                versionsOpen ? "font-medium text-accent" : "text-ink-muted"
              )}
              data-testid="writing-versions-toggle"
              aria-pressed={versionsOpen}
            >
              Cronologia
            </button>
          </div>
          <ExportMenu
            chapterId={chapter?.id}
            chapterExportDisabled={readOnly}
            onError={() => setSaveState("error")}
          />
          {!readOnly && chapter?.deletable ? (
            <ChapterDeleteButton
              chapterId={chapter.id}
              title={chapter.title}
              onDeleted={() => onChapterDeleted?.(chapter.id)}
            />
          ) : null}
          <SaveIndicator state={saveState} />
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col">
        {loading ? (
          <p className="p-4 text-sm text-ink-muted">Caricamento capitolo…</p>
        ) : chapterId && chapter ? (
          <>
            <div
              className={cn(
                "min-h-0 flex-1 flex-col",
                previewMode ? "hidden" : "flex"
              )}
            >
              <MarkdownEditor
                ref={editorRef}
                value={content}
                onChange={setContent}
                onSave={handleSave}
                readOnly={readOnly}
                activeSectionId={activeSectionId}
              />
            </div>
            {previewMode ? (
              <div
                className="min-h-0 flex-1 overflow-y-auto px-6 py-4"
                data-testid="writing-preview"
              >
                <ManuscriptMarkdown content={content} />
              </div>
            ) : null}
          </>
        ) : chapterId ? (
          <p className="p-4 text-sm text-ink-muted">Capitolo non trovato.</p>
        ) : (
          <p className="p-4 text-sm text-ink-muted">
            Scegli un capitolo dall&apos;outline per aprire l&apos;area di scrittura.
          </p>
        )}
      </div>

      {chapter && versionsOpen ? (
        <ChapterVersionsPanel
          open={versionsOpen}
          chapterId={chapter.id}
          expectedVersion={versionRef.current}
          onClose={() => setVersionsOpen(false)}
          onConflict={() => setConflictOpen(true)}
          onRestored={(updated) => {
            versionRef.current = updated.version;
            setChapter(updated);
            setContent(updated.content_md ?? "");
            setSaveState("saved");
            setPreviewMode(false);
            onChapterUpdated?.(updated);
          }}
        />
      ) : null}

      {chapter && (
        <footer className="flex shrink-0 items-center justify-between border-t border-border px-4 py-2 text-xs text-ink-subtle">
          <span>
            {activeSectionId ? `Sezione · ${sectionWords} parole` : "Sezione · —"}
          </span>
          <span>Capitolo · {chapterWords} parole</span>
        </footer>
      )}

      <ConflictDialog
        open={conflictOpen}
        onReload={() => void handleReload()}
        onOverwrite={() => void handleOverwrite()}
        onDismiss={() => setConflictOpen(false)}
      />

      <SourcePicker
        open={pickerOpen}
        onClose={() => setPickerOpen(false)}
        chapterId={chapterId}
        onSelectSource={(source) => {
          setPickerOpen(false);
          corpusClient.recordRecent(source.id);
          dispatchOpenFontePeek(source.id);
        }}
      />

      {findOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-ink/20 px-4 pt-[20vh]"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setFindOpen(false);
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Cerca nel capitolo"
            className="w-full max-w-md rounded-lg border border-border bg-surface p-4 shadow-md"
            data-testid="find-in-chapter-dialog"
          >
            <label className="block text-sm font-medium text-ink" htmlFor="find-in-chapter">
              Cerca nel capitolo
            </label>
            <input
              id="find-in-chapter"
              type="search"
              autoFocus
              value={findQuery}
              onChange={(event) => setFindQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Escape") setFindOpen(false);
              }}
              className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
              placeholder="Titolo sezione…"
            />
            <div className="mt-3 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setFindOpen(false)}
                className="rounded-md border border-border px-3 py-1.5 text-sm text-ink-muted"
              >
                Chiudi
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export { type MarkdownEditorHandle };
