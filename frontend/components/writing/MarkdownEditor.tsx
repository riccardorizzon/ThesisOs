"use client";

import {
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
  forwardRef,
} from "react";
import { cn } from "@/lib/cn";
import {
  INSERT_CITATION_EVENT,
  type InsertCitationDetail,
} from "@/lib/citationInsert";

export type MarkdownSection = {
  id: string;
  label: string;
  level: number;
  lineIndex: number;
};

export type SaveState = "idle" | "dirty" | "saving" | "saved" | "error";

export type MarkdownEditorProps = {
  value: string;
  onChange: (value: string) => void;
  onSave: (value: string) => Promise<void>;
  readOnly?: boolean;
  activeSectionId?: string;
  debounceMs?: number;
  className?: string;
  "data-testid"?: string;
};

export type MarkdownEditorHandle = {
  flushSave: () => Promise<boolean>;
  getSaveState: () => SaveState;
  scrollToSection: (sectionId: string) => void;
};

const DEFAULT_DEBOUNCE_MS = 3000;

/** Slug for heading anchor — preserves numeric prefixes like §3.2 */
export function sectionIdFromHeading(label: string): string {
  const normalized = label
    .trim()
    .replace(/^§\s*/, "")
    .toLowerCase()
    .replace(/[^\w\s.-]/g, "")
    .replace(/\s+/g, "-");
  return normalized || "section";
}

export function parseMarkdownSections(content: string): MarkdownSection[] {
  const sections: MarkdownSection[] = [];
  const lines = content.split("\n");
  lines.forEach((line, lineIndex) => {
    const match = line.match(/^(#{1,6})\s+(.+)$/);
    if (!match) return;
    const label = match[2].trim();
    sections.push({
      id: sectionIdFromHeading(label),
      label,
      level: match[1].length,
      lineIndex,
    });
  });
  return sections;
}

export function countWords(text: string): number {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}

export const MarkdownEditor = forwardRef<MarkdownEditorHandle, MarkdownEditorProps>(
  function MarkdownEditor(
    {
      value,
      onChange,
      onSave,
      readOnly = false,
      activeSectionId,
      debounceMs = DEFAULT_DEBOUNCE_MS,
      className,
      "data-testid": testId = "markdown-editor",
    },
    ref
  ) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [saveState, setSaveState] = useState<SaveState>("idle");
    const [focused, setFocused] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const savingRef = useRef(false);
    const valueRef = useRef(value);
    const onSaveRef = useRef(onSave);

    valueRef.current = value;
    onSaveRef.current = onSave;

    const sections = useMemo(() => parseMarkdownSections(value), [value]);

    const clearDebounce = useCallback(() => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
    }, []);

    const performSave = useCallback(async (): Promise<boolean> => {
      if (readOnly || savingRef.current) return saveState === "saved";
      clearDebounce();
      savingRef.current = true;
      setSaveState("saving");
      try {
        await onSaveRef.current(valueRef.current);
        setSaveState("saved");
        return true;
      } catch {
        setSaveState("error");
        return false;
      } finally {
        savingRef.current = false;
      }
    }, [clearDebounce, readOnly, saveState]);

    const scheduleSave = useCallback(() => {
      if (readOnly) return;
      clearDebounce();
      setSaveState("dirty");
      debounceRef.current = setTimeout(() => {
        void performSave();
      }, debounceMs);
    }, [clearDebounce, debounceMs, performSave, readOnly]);

    const scrollToSection = useCallback(
      (sectionId: string) => {
        const section = sections.find((s) => s.id === sectionId);
        const textarea = textareaRef.current;
        if (!section || !textarea) return;

        const lines = value.split("\n");
        let charOffset = 0;
        for (let i = 0; i < section.lineIndex && i < lines.length; i++) {
          charOffset += lines[i].length + 1;
        }
        textarea.focus();
        textarea.setSelectionRange(charOffset, charOffset);
        const lineHeight = parseInt(getComputedStyle(textarea).lineHeight, 10) || 20;
        textarea.scrollTop = Math.max(0, section.lineIndex * lineHeight - 40);
      },
      [sections, value]
    );

    useImperativeHandle(
      ref,
      () => ({
        flushSave: performSave,
        getSaveState: () => saveState,
        scrollToSection,
      }),
      [performSave, saveState, scrollToSection]
    );

    useEffect(() => {
      if (activeSectionId) scrollToSection(activeSectionId);
    }, [activeSectionId, scrollToSection]);

    useEffect(() => () => clearDebounce(), [clearDebounce]);

    const insertTextAtCursor = useCallback(
      (text: string) => {
        const textarea = textareaRef.current;
        if (!textarea || readOnly) return;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const current = valueRef.current;
        const next = `${current.slice(0, start)}${text}${current.slice(end)}`;
        onChange(next);
        scheduleSave();
        requestAnimationFrame(() => {
          const pos = start + text.length;
          textarea.focus();
          textarea.setSelectionRange(pos, pos);
        });
      },
      [onChange, readOnly, scheduleSave]
    );

    useEffect(() => {
      const onInsertCitation = (event: Event) => {
        const detail = (event as CustomEvent<InsertCitationDetail>).detail;
        if (!detail?.marker) return;
        const suffix = detail.quote ? ` "${detail.quote.slice(0, 80)}"` : "";
        insertTextAtCursor(`${detail.marker}${suffix} `);
      };
      window.addEventListener(INSERT_CITATION_EVENT, onInsertCitation);
      return () => window.removeEventListener(INSERT_CITATION_EVENT, onInsertCitation);
    }, [insertTextAtCursor]);

    const handleChange = (next: string) => {
      onChange(next);
      scheduleSave();
    };

    return (
      <div
        className={cn(
          "flex flex-1 flex-col",
          focused && "ring-2 ring-accent/30 ring-offset-1 rounded-md",
          className
        )}
        data-testid={testId}
      >
        <textarea
          ref={textareaRef}
          value={value}
          readOnly={readOnly}
          aria-label="Contenuto capitolo"
          onChange={(e) => handleChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={cn(
            "mx-auto w-full max-w-[70ch] flex-1 resize-none bg-transparent px-4 py-3",
            "font-mono text-sm leading-relaxed text-ink",
            "focus:outline-none",
            readOnly && "cursor-default opacity-90"
          )}
          spellCheck
        />
        <div
          className="sr-only"
          aria-live="polite"
          data-testid="markdown-editor-save-state"
          data-save-state={saveState}
        >
          {saveState}
        </div>
        <div className="sr-only" data-testid="markdown-editor-sections">
          {sections.map((s) => (
            <span key={s.id} id={`section-${s.id}`} data-section-id={s.id}>
              {s.label}
            </span>
          ))}
        </div>
      </div>
    );
  }
);

export function saveStateLabel(state: SaveState): string | null {
  switch (state) {
    case "saving":
      return "Salvataggio…";
    case "saved":
      return "Salvato";
    case "dirty":
    case "error":
      return "Non salvato";
    default:
      return null;
  }
}
