# Intent Resolver

There are no commands. Read the free text after `ASEP` and deduce **one** intent.

| Intent | Natural-language cues (it/en) | Pipeline |
|--------|------------------------------|----------|
| `develop` | implementa, sviluppa, build, continua, riprendi, prossima milestone, next | capability → governance → work-order → execute → qualify (light) → commit → report |
| `review` | review, rivedi, controlla, valuta questa PR/diff | governance + ADC review of a diff/PR; **no implementation** |
| `design` | progetta, design, esplora, architettura, valuta opzioni | investigation (plan mode); produce ADR/plan draft; **no implementation** |
| `qualify` | qualifica, qualify, benchmark, dogfood, eval | run the qualification gates for the current capability |
| `promote` | promuovi, promotion, freeze, tag, chiudi milestone | run the promotion stage |
| `status` | continua senza oggetto, dove siamo, status, stato | read context, report the next ready capability; **no implementation** |

Rules:
- `continua <capability/milestone>` → `develop` that capability.
- `continua` with no object → resolve the next `ready` capability (see capability resolver); if found, `develop` it; else `status`.
- When genuinely ambiguous → default to `status` (report, never implement).
- `design`/`review` never write product code.

Emit a one-line resolution: `intent: <type>` before proceeding.
