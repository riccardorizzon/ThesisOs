# Intent Resolver

Read the request and deduce **one** intent. Two operator surfaces exist:

1. **Architect API** — structured authorization (see `resolvers/authorize.md`)
2. **Natural language** — free text after `ASEP` or plain operator message

| Intent | Cues (it/en) | Pipeline |
|--------|--------------|----------|
| `authorize` | `AUTHORIZE PX-3`, `AUTHORIZE PROGRAM PX-3`, `# ARCHITECT AUTHORIZATION` + Program field | **authorize.md** → pre-flight → first EWO → develop (conformance or engineering) |
| `develop` | implementa, sviluppa, build, continua, riprendi, prossima milestone, next | capability → governance → work-order → execute → qualify (light) → commit → report |
| `review` | review, rivedi, controlla, valuta questa PR/diff | governance + ADC review of a diff/PR; **no implementation** |
| `design` | progetta, design, esplora, architettura, valuta opzioni | investigation (plan mode); produce ADR/plan draft; **no implementation** |
| `qualify` | qualifica, qualify, benchmark, dogfood, eval | run the qualification gates for the current capability |
| `promote` | promuovi, promotion, freeze, tag, chiudi milestone | run the promotion stage |
| `status` | continua senza oggetto, dove siamo, status, stato | read context, report the next ready capability; **no implementation** |

Rules:
- **`AUTHORIZE <program>`** (any syntax in `authorize.md`) → `authorize` **before** any other intent. Do not treat as briefing — execute the authorization pipeline.
- `continua <capability/milestone>` → `develop` that capability.
- `continua` with no object → resolve the next `ready` capability (see capability resolver); if found, `develop` it; else `status`.
- When genuinely ambiguous → default to `status` (report, never implement).
- `design`/`review` never write product code.

Emit a one-line resolution: `intent: <type>` before proceeding.
