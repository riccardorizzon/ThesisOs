# Writing Workspace — Design Overrides (PX-2)

> **Routes:** `/writing`, `/writing/[chapterId]`  
> **Product spec:** `docs/product/specs/px2-research-workspace-experience.md` §4.3, §7  
> **UI spec:** `design-system/thesisos/px2-research-workspace-ui-spec.md` §5

---

## Layout (frozen three-panel)

```text
ContextBar (full width)
┌──────────────┬────────────────────────────┬──────────────────┐
│ Outline      │ Editor                     │ Right rail       │
│ 240px        │ min 480px · flex-1         │ 320px · tabbed   │
└──────────────┴────────────────────────────┴──────────────────┘
Linked sources footer (collapsible)
```

| Panel | Token | Collapse |
|-------|-------|----------|
| Outline | `--outline-width` | `⌘\` |
| Editor | `flex-1 min-w-editor` | — |
| Right rail | `--rail-width` | `⌘⇧\` |

Gap between panels: `--space-3` (12px) at ≥1280px; `--space-4` at smaller desktop.

---

## Right rail tabs (single slot)

| Order | Tab | Shortcut | Default |
|-------|-----|----------|---------|
| 1 | AI | ⌘1 | ✓ |
| 2 | Contesto | ⌘2 | |
| 3 | Fonte | ⌘3 | Opens when source peeked |
| 4 | Revisione | ⌘4 | |

Switching tabs preserves editor selection and scroll.

---

## Editor chrome

| Zone | Height | Content |
|------|--------|---------|
| Toolbar | 40px | Cita, Find, Preview |
| Header | 48px | Chapter title, save state |
| Body | flex | Markdown, max 70ch centered |
| Footer | 32px | Word counts |

Save copy: `Salvato` · `Salvataggio…` · `Non salvato`

---

## Outline

- Row: `--row-height-dense` (36px)
- Status badges: Bozza / In revisione / Approvato
- Filter: Tutti / In corso / Da revisionare
- No drag reorder (PX-6)

---

## Empty states

| Surface | Copy | CTA |
|---------|------|-----|
| No chapter | "Scegli un capitolo dall'outline" | — |
| Empty editor | "Inizia a scrivere §1" | Optional template |
| AI panel | "Seleziona un passaggio o usa un'azione di capitolo" | Action list |
| Fonte tab | "Apri una fonte con Cita o Trova fonti" | Cita fonte |

---

## URL state

`/writing/[chapterId]?section=3.2&source=src-id&panel=fonte`

---

## Components

| Block | Component |
|-------|-----------|
| Layout | `WritingWorkspace` |
| Outline | `WritingOutline` |
| Editor | `WritingEditorShell` + `MarkdownEditor` |
| Rail | `RightRail`, `RailTabs` |
| AI | `WritingAiPanel` (extend) |
| Inspector | `ContextInspector` |
| Peek | `SourceReader` (compact) |
| Context | `ContextBar` |
