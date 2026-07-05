# Qualification WorkOrder Proposal — C.6

> **Status:** ✅ **Approved** (2026-06-30) — conditions: C.6.2 corpus-use-only · W-01…W-12 observable  
> **Pre-flight:** ✅ `.asep/reports/C.6-preflight-runtime-audit.md` · **Measured Runtime Coverage: 85%**  
> **C.6-R1:** ✅ executed — **PARTIAL (REJECT)** · **EWO-7B** implemented 2026-07-01  
> **C.6-R2:** pending — post-EWO-7B re-QWO
>
> **META-1:** ✅ baseline · **Qualified invariants:** OR-3, OR-4, OR-5  
> **Program:** `.asep/programs/thesis-agent-migration.yaml`  
> **Spec instance:** `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-6  
> **Template:** `.asep/templates/qualification-work-order-template.md`

### Review index (required deliverables)

| # | Deliverable | Section |
|---|-------------|---------|
| 1 | Qualification Contract | §4 |
| 2 | Qualification WorkOrder | §5 |
| 3 | Expected Evidence | §6 |
| 4 | PASS criteria | §4.6 |
| 5 | FAIL criteria | §4.8 |
| 6 | Qualification Coverage | §7.1 |
| 7 | Traceability Coverage metric | §7.2 |
| 8 | Writing FAIL test cases | §8 |
| 9 | Composite capability aggregation rule | §9 |
| 10 | Required EWOs if qualification fails | §10 |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.6 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Platform capability class** | **Academic Artifact Production** |
| **Knowledge domain** | **Procedural** (constrained writing execution) |
| **Graph node** | `or-6-write-paragraph` |
| **QWO sensitivity** | **Reasoning-sensitive** |
| **Lifecycle transition** | `specified` → **`approved`** (2026-06-30) → `qualified` (on C.6-R1 PASS only) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-5-decisions` **qualified** (C.5-R1 PASS, 2026-06-30) |
| **First run id** | `C.6-R1` (on approval) |

---

## 1. Platform objective (ASEP — program-agnostic)

Qualify the generic ASEP capability **Academic Artifact Production**:

> Given **qualified upstream invariants**, the live runtime can **produce a bounded
> academic artifact** (e.g. one paragraph) that conforms to **active procedural, normative,
> and organizational constraints** — without re-demonstrating corpus utilization,
> constraint compliance, or decision lifecycle integrity.

OR-6 tests **production under constraint**, not re-qualification of OR-3/4/5.

### 1.1 Qualified invariants (assumed — not re-tested as primary scope)

| Prior gate | Invariant assumed in OR-6 |
|------------|---------------------------|
| **OR-3** qualified | Active corpus only; CORPUS-02/03 excluded; library-first discipline |
| **OR-4** qualified | Normative rules applicable in prose (autore-date, no footnotes, R1–R5 where relevant) |
| **OR-5** qualified | Frozen decisions respected; no unilateral unfreeze; Decision Consistency |

**Regression rule:** if output **violates** an OR-3/4/5 invariant, classify as **Invariant
Regression** (record + fail parent if material) — not as primary Writing FAIL taxonomy item.
OR-6 does **not** spawn corpus/normative/decision EWOs unless investigation shows **production-path**
failure, not prior-capability drift.

### 1.2 What OR-6 tests (primary scope)

| Layer | Question |
|-------|----------|
| **Production mode** | Academic register; persona/firewall OFF in writing mode |
| **Procedural synthesis** | A/B separation; REV-006; evidence levels where required |
| **Artifact boundaries** | Status label (bozza / PRONTO PER REVISIONE); no unilateral congelamento |
| **Controlled sources** | Paragraph cites only admissible authors for the assigned section |

**Not in scope:** listing corpus (OR-3), listing rules (OR-4), listing decisions (OR-5),
memory update protocol (OR-7), E2E session flow.

---

## 2. Program instance binding (ThesisOS migration — not ASEP core)

| Abstract (ASEP) | ThesisOS instance |
|-----------------|---------------------|
| **Production target** | One paragraph for **§3.2 colore / Josef Albers** (Outline-Master cap. 3) |
| **Procedural GT** | `02_METHOD/Writing-Rules.md`, `Revision-Workflow.md`, `01_SYSTEM/Persona.md` (firewall) |
| **Normative GT (applied)** | Qualified OR-4 — UNI-01 §8, RED-02, REL-01 R1–R5 |
| **Corpus GT (applied)** | Qualified OR-3 — Albers active; Mythologies/Bourriaud excluded |
| **Organizational GT (applied)** | Qualified OR-5 — outline frozen; no new sections |
| **Structural context** | `03_PROJECT/Outline-Master.md` § cap. 3 |

**Canonical QWO prompt (instance — fixed for reproducibility):**

```text
Scrivi un paragrafo di prova per §3.2 colore e Josef Albers in modalità scrittura
accademica. Applica REV-006, separazione A/B, livelli FONDATO/PLAUSIBILE dove
pertinente, firewall persona OFF. Etichetta lo stato del testo.
```

**Evaluator oracle (instance):** output paragraph only + `Writing-Rules.md`, `Revision-Workflow.md`,
`Relatrice-Rules.md`, `Persona.md`, Outline §3.2, `Bibliography-Master` (Albers), Decisions REV-006.

---

## 3. Composite capability decomposition

Parent node: **`or-6-write-paragraph`** (composite).

| Sub-capability | ASEP meaning | ThesisOS QWO signal |
|----------------|--------------|---------------------|
| **C.6.1 Production Mode** | Academic register; persona OFF | No emoji/exclamations; neutral third person; no cheerleader voice |
| **C.6.2 Source-Constrained Synthesis** | **Use** of OR-3-qualified corpus in prose (not re-qualification) | Albers in Blocco A; tesi in Blocco B; no excluded authors in text |
| **C.6.3 Normative Conformance in Prose** | Active norms applied **in the artifact** | Autore-date; no piè di pagina (OR-4 invariant) |
| **C.6.4 Probative Labeling** | Status + evidence level discipline | bozza or PRONTO PER REVISIONE; FONDATO/PLAUSIBILE/SPECULATIVO |

**C.6.2 — architectural condition (approval gate):**

C.6.2 verifies that the runtime **employs** a corpus already qualified by OR-3 when synthesizing
prose. It does **not** re-test corpus completeness, exclusion listing, or retrieval coverage.
Failure to cite Albers when writing §3.2 is a **Writing FAIL**; failure to list 12 authors is
**out of scope** (OR-3).

**Boundary:** C.6.2 checks **use in prose**, not corpus listing (OR-3). C.6.3 checks **embedded
conformance**, not rule enumeration (OR-4).

---

## 3.1 Runtime Coverage — governance rule

Same as C.4/C.5: **measured at pre-flight**; authorizes C.6-R1; not a PASS presupposition.

### 3.2 Artifact Issue taxonomy (parallel — unchanged)

Record ID slips / formatting under **Artifact Issue** — not Writing FAIL. See C.5 §3.3.

---

## 4. Qualification Contract

### 4.1 Capability

`or-6-write-paragraph` — **Academic Artifact Production** under qualified invariants.

### 4.2 Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| `or-3` qualified | C.3-R4 PASS | capability graph |
| `or-4` qualified | C.4-R1 PASS | capability graph |
| `or-5` qualified | C.5-R1 PASS | capability graph |
| Phase B + EWO chain | Writing-related memories/docs promoted | promotion-log, EWO-1/2/3 |
| Live stack | `/health` → 200 | pre-flight |
| **Pre-flight audit** | Measured Runtime Coverage | `.asep/reports/C.6-preflight-runtime-audit.md` |
| Proposal approved | this document → approved | **User explicit approval** |

### 4.3 Ground Truth — controlled inputs (evaluator)

**Platform rule:** QWO fixes **inputs** so production is reproducible. Swapping section/author
requires a new proposal or explicit contract amendment.

**ThesisOS binding — inputs frozen for C.6-R1:**

| Input | Value | Role |
|-------|-------|------|
| **Section** | §3.2 colore · Josef Albers | Outline-Master cap. 3 |
| **Mode** | Scrittura accademica | Persona OFF |
| **Author (corpus)** | Josef Albers — *Interaction of Color* | Active support author (OR-3 invariant) |
| **Excluded** | Barthes *Mythologies*, Bourriaud | Must not appear in prose |
| **REV-006** | A/B + FONDATO/PLAUSIBILE/SPECULATIVO | Binding decision |
| **Normative** | autore-date; no footnotes (UNI-01 §8, RED-02) | OR-4 invariant applied in text |
| **Status rule** | bozza or PRONTO PER REVISIONE only | No unilateral «congelato» |

**Mandatory oracle elements for PASS (W-01…W-12):**

All criteria are **binary and observable** — evaluator marks PASS/FAIL per row from output text
only. No subjective quality judgments («scrittura buona», «tono adeguato»).

| ID | Observable criterion | PASS when (verifiable) | Sub-cap |
|----|---------------------|------------------------|---------|
| W-01 | Paragraph exists | ≥ **80 words** of connected prose (not list-only); **≥1** mention of `Albers` or `colore` | C.6.2 |
| W-02 | Persona OFF | **Zero** emoji (Unicode `\p{Emoji}`); **zero** `!`; **zero** matches from persona blocklist §4.3.1 | C.6.1 |
| W-03 | A/B separation | **≥1** theory-attribution cue (`Secondo Albers`, `Albers sostiene`, `Blocco A`) **and** **≥1** application cue (`nella tesi`, `applicazione`, `Blocco B`, `STIGMATA`, `caso studio`) | C.6.2 |
| W-04 | Attribution marker | Every sentence with Albers as theoretical source includes `(Albers,` **or** `Secondo Albers` **or** explicit `FONDATO`/`PLAUSIBILE`/`SPECULATIVO` tag | C.6.2 |
| W-05 | Evidence level tag | If interpretive claim without direct quote: contains **≥1** of `FONDATO`, `PLAUSIBILE`, `SPECULATIVO` (case-insensitive) | C.6.4 |
| W-06 | Autore-date | Contains `(Albers,` + 4-digit year **or** `Albers (` + year pattern | C.6.3 |
| W-07 | No footnotes | **Absent:** `piè di pagina`, `nota a piè`, `[^`, markdown footnote `^1` | C.6.3 |
| W-08 | Status label | Contains substring `bozza` **or** `PRONTO PER REVISIONE` (case-insensitive) | C.6.4 |
| W-09 | No unilateral freeze | **Absent** as status of this text: `congelato`, `congelata`, `congelato il paragrafo` | C.6.4 |
| W-10 | Excluded authors | **Absent:** `Mythologies`, `Bourriaud` (case-insensitive) | IR (OR-3) |
| W-11 | Source anchor | **≥1** of: `[n]` citation marker, `Interaction of Color`, `Interazione del colore` | C.6.2 |
| W-12 | Academic language | **≥3** Italian function tokens among {` di `, ` che `, ` nel `, ` della `, ` come `}; **zero** persona blocklist matches | C.6.1 |

#### 4.3.1 Persona blocklist (evaluator — fixed strings)

`let's go`, `we move`, `okay, good`, `boss fight`, `recovery mode`, `🔥`, `⚡`, `💥`, `🫡`, `🎯`, `🏁`

**Not evaluated:** literary quality, stylistic elegance, relatrice tonal preference beyond
observable R1 (first full name on first Albers mention — optional W-13 Artifact Issue if missing).

### 4.4 Runtime Boundary

**Agent under test must NOT use:**

- Workspace blueprint files directly
- `_inbox/kimi-claw/` export
- Web / external sources
- Operator paste of paragraph draft
- File attachments on `/chat`

**Allowed runtime surfaces:**

| Surface | Role |
|---------|------|
| M2 memories | thesis, decisions, editable, university-rules, relatrice-rules |
| M3/M4 | Albers OCR, Outline-Master, Writing-Rules if promoted |
| M6 chapters | Context only — not substitute for new paragraph production |

**Hard constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### 4.5 Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.6-preflight-runtime-audit.md` | Measured procedural/runtime coverage |
| `.asep/reports/C.6-R{k}.md` | Prompt, **full paragraph output**, oracle matrix, Writing FAIL + regression flags, verdict |
| `.asep/certificates/C.6-R{k}-<date>.yaml` | QC Certificate |
| `operational-readiness-log.md` | OR-6 row |
| Capability graph | `academic_production.*`, `coverage`, `qualification_runs[]` |

**Optional artifact:** paragraph text excerpt in report (required for evaluation; not a chapter commit).

### 4.6 PASS Criteria

**Composite rule:** parent PASS ⟺ all C.6.1–C.6.4 PASS + no **material Invariant Regression**
+ Traceability ≥ threshold.

**Parent checklist:**

1. W-01…W-12 satisfied on produced paragraph.
2. **Does not** primarily re-list corpus, rules, or decisions (OR-3/4/5 boundary).
3. Runtime boundary respected.
4. Traceability Coverage ≥ 80% on **claims within the paragraph**.

**Sub-cap PASS signals:**

| Sub-cap | PASS when |
|---------|-----------|
| **C.6.1 Production Mode** | W-02, W-12 satisfied (binary) |
| **C.6.2 Source-Constrained Synthesis** | W-01, W-03, W-04, W-11 satisfied; W-10 absent (corpus **use**, not OR-3 re-test) |
| **C.6.3 Normative Conformance in Prose** | W-06, W-07 satisfied in artifact |
| **C.6.4 Probative Labeling** | W-05, W-08, W-09 satisfied |

→ `or-6-write-paragraph` lifecycle → **`qualified`**; OR-7 unblocked.

### 4.7 PARTIAL Criteria

- Paragraph produced but A/B or status label incomplete.
- Register OK but missing autore-date or one normative element in prose.
- Reasoning variance (W-03 borderline) without invariant regression.
- Traceability 60–79%.
- **Does not** advance lifecycle without operator disposition.

### 4.8 FAIL Criteria

| Class | FAIL when |
|-------|-----------|
| **Writing FAIL** | Primary procedural failure (register, A/B, labeling) — see §8 |
| **Invariant Regression** | Material OR-3/4/5 violation **in produced text** (W-10, footnotes, unfreeze) |
| **Structural** | Cannot produce paragraph traceable to promoted writing/corpus surfaces |
| **Behavioral** | Non-deterministic register/A/B without structural cause |
| **Governance** | Unilateral GT/chapter mutation attempted |

**No production** (empty or non-academic reply) → **Writing FAIL** (C.6.1/C.6.2).

### 4.9 Spawn Rule (EWO)

```text
QWO C.6-Rk → FAIL or PARTIAL
        → Classify (Writing | Invariant Regression | Structural | Behavioral | Governance)
        → If Invariant Regression → investigate: production path vs prior-capability drift
        → EWO-7A or EWO-7B (not EWO-3/4/5/6 unless investigation proves upstream drift)
        → re-QWO C.6-R{k+1}
```

**Reasoning-sensitive:** one re-QWO without remediation acceptable only if Traceability OK
and failure is pure variance — document in report.

### 4.10 Lifecycle Transition

| Verdict | Lifecycle | Unblocks |
|---------|-----------|----------|
| **PASS** | → `qualified` | C.7 / OR-7 |
| **PARTIAL** | unchanged | operator disposition |
| **FAIL** | unchanged | EWO if structural/writing path |

---

## 5. Qualification WorkOrder (execution definition)

**Gate:** pre-flight measured coverage recorded before C.6-R1.

| Phase | Action | Mutations |
|-------|--------|-----------|
| PLAN | Proposal approved + pre-flight complete | none |
| QC | Certificate `.asep/certificates/C.6-R1-<date>.yaml` | none |
| POLICY | Level 2 QWO auto-auth if clauses met | none |
| EXECUTE | POST `/chat` canonical prompt; new session | none |
| VERIFY | Oracle W-01…W-12; sub-cap matrix; Writing FAIL §8 | none |
| REPORT | `.asep/reports/C.6-R1.md`; log + graph | evidence only |
| STOP | PARTIAL/FAIL → disposition | — |

---

## 6. Expected evidence

```text
C.6-preflight-runtime-audit.md
        ↓
C.6-R1.md
├── Controlled inputs (§4.3) confirmed
├── Canonical prompt (verbatim)
├── Paragraph output (full text)
├── Sub-cap matrix C.6.1–C.6.4
├── Oracle W-01…W-12
├── Writing FAIL results (§8)
├── Invariant Regression flags (if any)
├── Traceability worksheet
├── Artifact Issues (if any)
└── Verdict

operational-readiness-log.md → OR-6
capability graph → academic_production{}, qualification_runs[]
```

---

## 7. Qualification Coverage & Traceability

### 7.1 Five dimensions

| Dimension | Pre-flight | QWO report |
|-----------|------------|------------|
| Ground Truth Coverage | 100% (writing + outline + Albers in repo) | confirm |
| Runtime Coverage | *measured pre-flight* | re-measure |
| Qualification Coverage | pending | PASS/PARTIAL/FAIL |
| Evidence Coverage | pending | report + log |
| Traceability Coverage | pending | §7.2 |

**Informative estimate (pre-flight audit required):**

| Element | Expected |
|---------|----------|
| Albers OCR indexed | ✅ Fase B |
| Outline-Master | ✅ EWO-1 |
| M2 editable / writing rules | partial via editable |
| Persona firewall in prompt path | audit required |

### 7.2 Traceability Coverage (paragraph-scoped)

**Definition:** each **claim** in the paragraph maps to:

```text
Claim → [n] source OR Blocco A/B label OR FONDATO/PLAUSIBILE tag
      → promoted runtime artifact (Albers OCR, outline, decisions)
```

| Threshold | Impact |
|-----------|--------|
| ≥ **80%** | Required for PASS |
| 60–79% | PARTIAL candidate |
| < 60% | FAIL or PARTIAL |

---

## 8. Writing FAIL test cases (primary — not invariant regression)

Evaluator applies to **produced paragraph** only.

| ID | Scenario | Expected | If violated → |
|----|----------|----------|---------------|
| **WF-01** | Persona bleed | No emoji/exclamations/cheerleader | **Writing FAIL** C.6.1 |
| **WF-02** | Register | Italian academic neutral | **Writing FAIL** C.6.1 |
| **WF-03** | A/B collapse | Albers vs tesi not separated | **Writing FAIL** C.6.2 |
| **WF-04** | Ghost attribution | Claim without source or level | **Writing FAIL** C.6.2 |
| **WF-05** | Missing status | No bozza/PRONTO PER REVISIONE | **Writing FAIL** C.6.4 |
| **WF-06** | Unilateral freeze | Text labeled congelato | **Writing FAIL** C.6.4 |
| **WF-07** | No paragraph | List/rules instead of prose | **Writing FAIL** C.6.2 |
| **WF-08** | Wrong section | Ignores §3.2/Albers brief | **Writing FAIL** C.6.2 |

**Invariant Regression (separate flags — not WF taxonomy):**

| ID | Scenario | Class |
|----|----------|-------|
| **IR-01** | Mythologies/Bourriaud in prose | OR-3 regression |
| **IR-02** | Footnotes proposed/used | OR-4 regression |
| **IR-03** | Suggests reopening frozen outline/corpus | OR-5 regression |

Material **IR-*** → parent FAIL even if WF clean.

---

## 9. Composite aggregation rule

```text
or-6-write-paragraph.qualified  ⟺  latest QWO PASS
                                   AND C.6.1…C.6.4 PASS
                                   AND no material Invariant Regression
                                   AND Traceability ≥ 80%
```

Record on graph:

```yaml
academic_production:
  c6_1_production_mode: …
  c6_2_source_constrained_synthesis: …
  c6_3_normative_conformance_in_prose: …
  c6_4_probative_labeling: …
```

---

## 10. Required EWOs if qualification fails

| FAIL class | EWO | Category |
|------------|-----|----------|
| **Structural** | **EWO-7A** Procedural Alignment — promote Writing-Rules, Revision-Workflow, persona firewall hints to runtime | Alignment |
| **Writing / Production path** | **EWO-7B** Academic Production Path — writer route, mode flag, procedural block in prompt | **Production Path** |
| **Invariant Regression** | Investigate first — fix production path unless proven upstream drift | rarely EWO-3/4/5/6 |
| **Behavioral** | Document variance; single re-QWO if justified | rarely EWO |

### EWO-7A (Alignment)

Promote/index `Writing-Rules.md`, `Revision-Workflow.md`; verify editable memory; no GT edits.

### EWO-7B (Production Path)

Academic mode in prompt hierarchy; ensure `/chat` writing prompt activates procedural + normative
blocks without re-running OR-3/4/5 list tests; optional writer-route smoke.

**Not Grounding** (OR-3 class) unless investigation proves retrieval-only failure for Albers in
writing turn.

---

## Scope

### In scope (after approval)

- Pre-flight audit
- C.6-R1 QWO + report + log

### Out of scope

- QWO execution now
- Chapter commit to M6
- OR-7, E2E
- Re-qualifying OR-3/4/5

---

## Impact analysis

| Layer | Impact |
|-------|--------|
| Product runtime | None during QWO |
| ASEP | Extends capability model §4C; assumes qualified invariants |

## Approval gate

```text
User: C.6: approved  ✅ 2026-06-30
  → pre-flight authorized (this step)
  → C.6-R1 authorized only after pre-flight measured + operator disposition
  → FAIL/PARTIAL → STOP + disposition
```

**Limitations (operator disposition):**

- Proposal approval ≠ OR-6 qualified.
- C.6-R1 requires dedicated QWO + PASS/FAIL report.
- Operational Readiness subordinate to OR-6, OR-7, E2E PASS.

---

## Compatibility checklist

| Invariant | Status |
|-----------|--------|
| OR-3/4/5 not re-tested as primary scope | ✅ §1.1 |
| Capability independence | ✅ Writing FAIL vs Invariant Regression |
| Engineering State Machine | ✅ |
| WO-TRACE | ✅ |
| E2E remains integration gate | ✅ not replaced by OR-6 |

---

## Recommended next action

1. ~~User approves~~ ✅ **2026-06-30** (C.6.2 corpus-use · observable W oracle)
2. Execute **C.6 pre-flight** (measured coverage)
3. **C.6-R1** — after pre-flight + explicit authorization; dedicated QWO + report
4. PASS → C.7 proposal; FAIL → EWO-7A/7B per classification
