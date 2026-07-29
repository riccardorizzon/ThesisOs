# OpenWorker study notes — Writing Action Loop (Phase 0)

- **Date:** 2026-07-29
- **Purpose:** Capture what ThesisOS adopts from [OpenWorker](https://github.com/andrewyng/openworker) for the Writing panel loop. Patterns only — no product import.

---

## What OpenWorker is

Local-first desktop AI coworker (Tauri + Python server). Engine built on **aisuite**. Delivers finished work via tool loop, not chat-only.

## Files worth reading

| Path | ThesisOS takeaway |
|------|-------------------|
| `coworker/engine.py` | `TurnEngine`: async model↔tool loop, max iterations, approval injection |
| `coworker/tools/registry.py` | `ToolRegistry`: schemas + execute |
| `coworker/risk.py` | Four risk classes; `classify(tool_name)` |
| `coworker/permissions.py` | `Decision(allowed, needs_user)` per call |
| `coworker/tools/plan.py` | `propose_plan` = out-of-band approval before mode switch |
| `coworker/mcp/` | **Skip for v1** — MCP not in ThesisOS product runtime |

## Patterns to adopt (ThesisOS v1)

1. **Registry + loop** — not aisuite dependency
2. **Risk taxonomy** — v1 all `read` for panel tools
3. **Two-phase pipeline** — retrieval loop then existing writer (ThesisOS-specific; OpenWorker merges in one loop)
4. **Iteration cap** — OpenWorker ~12; ThesisOS v1 uses **6** for panel latency

## Patterns to skip

- Desktop shell, Tauri, local filesystem tools
- MCP client, OAuth connectors, automations scheduler
- Multi-provider router (ADR-0002 Vertex-only)
- aisuite / openworker pip packages in `backend/app/`

## aisuite note

OpenWorker README points to aisuite for reusable harness. For ThesisOS, **read aisuite docs** if tool-schema generation becomes painful; do not add as runtime dep without ADR.

## Mapping to ThesisOS today

| OpenWorker | ThesisOS today | After Phase 3 |
|------------|----------------|---------------|
| Tool loop | Single search + generate | Loop for verify/find-sources |
| Approval inbox | Proposal queue | Unchanged for writes |
| Risk engine | Implicit (all read via API) | Explicit `action_loop/permissions.py` |
| Planner | N/A | Still deferred (M12 graph) |

---

**Next:** ADR-0049 + implementation plan Phase 1.
