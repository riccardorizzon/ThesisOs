# PX-6 — Polish Experience UI Specification

> **Status:** DRAFT — UX handoff (PX6-EWO-001)  
> **Product source:** [`docs/product/specs/px6-polish-experience-v1.md`](../../docs/product/specs/px6-polish-experience-v1.md)  
> **Tokens:** [`docs/product/design-system-v1.md`](../../docs/product/design-system-v1.md)  
> **Typography:** [`MASTER.md`](MASTER.md) PX-6 phase

---

## 0. UX Alignment Review — PASS (draft)

| Check | Result |
|-------|--------|
| Spec citation | `px6-polish-experience-v1.md` |
| Capabilities PX-6.1…PX-6.7 | Product §2 |
| Milestone boundary | PX-6 only; no PX-5 canvas expansion |
| W-06 mitigation UX | Product §4–5 |

---

## 1. Design foundations

Inherits frozen tokens. PX-6 adds validator and export tokens only.

| Token | Value | Usage |
|-------|-------|-------|
| `--cite-valid` | `--color-success` | Valid author-date highlight |
| `--cite-invalid` | `--color-warning` | Numeric `[n]` highlight |
| `--cite-review` | `--color-ink-muted` | Needs review underline |

### Typography (PX-6 phase)

| Role | Font | Loading |
|------|------|---------|
| Headings | Crimson Pro | `next/font/google` |
| Body | Atkinson Hyperlegible | `next/font/google` |

---

## 2. Citation validator UI

### 2.1 Inline editor (`MarkdownEditor`)

```text
Invalid [2] segment → amber underline + tooltip "Citazione numerica — usa (Autore, Anno)"
Valid (Albers, 1963) → no highlight
```

### 2.2 AI panel (`WritingAiPanel`)

```text
┌─ Azioni AI ─────────────────────────┐
│ ⚠ 2 citazioni da verificare          │  ← banner when issues
│ [stream output with highlights]       │
│ [Annulla] [Applica] (disabled)       │  ← until resolved or override
│ [Applica comunque]                    │  ← secondary when override allowed
└───────────────────────────────────────┘
```

### 2.3 Sources Bibliografia

Export button + format picker; print action; invalid cite count badge.

---

## 3. Project switcher (`ProjectSwitcher`)

```text
┌─ Progetto ──────────────────────────┐
│ ▾ Tesi di laurea (thesis-agent)     │
│   ─────────────────────────────     │
│   + Nuovo progetto                  │
└─────────────────────────────────────┘
```

Active project persists; all module API calls use `project_id`.

---

## 4. Settings (`/settings`)

```text
┌─ Settings ──────────────────────────────────────────┐
│ Progetto                                            │
│   Nome visualizzato    [________________]           │
│   ID progetto          thesis-agent (read-only)     │
│                                                     │
│ Citazioni                                           │
│   Stile preferito      ( ) Autore-data  ( ) APA     │
│                                                     │
│ Export                                              │
│   Formato default      [ BibTeX ▾ ]                 │
│                                                     │
│ Scorciatoie                                         │
│   [ Apri palette comandi ]                          │
└─────────────────────────────────────────────────────┘
```

---

## 5. Outline reorder (`WritingOutline`)

- Drag handle on chapter rows (desktop ≥1024px)
- Drop indicator between rows
- `aria-grabbed` / `aria-dropeffect` for a11y
- Mobile: read-only order message

---

## 6. Print stylesheet

`@media print` for Bibliografia tab — hide AppShell chrome, academic ordering.

---

## 7. PX-6 exclusions (UI)

| Feature | Owner |
|---------|-------|
| Canvas new features | PX-5 complete |
| Collaboration UI | Out of scope |
| Agent topology changes | ADR supersession |
