# Integration Review — PX2 Integration {A|B|C}

> **Type:** Integration barrier (not EWO)  
> **Supervisor:** Engineering Supervisor  
> **Depends on:** Wave {A|B|C} all WorkOrders implementation-complete

---

## Identity

| Field | Value |
|-------|-------|
| **Integration id** | PX2-INTEGRATION-{A|B|C} |
| **Wave completed** | wave_{a|b|c} |
| **WorkOrders merged** | {list} |

---

## Merge checklist

- [ ] Worktrees merged in `merge_order` from `px2-parallel.yaml`
- [ ] No cross-ownership file conflicts unresolved
- [ ] Cross-slice wiring completed (see wave-specific actions below)
- [ ] `make ci` green on integrated branch
- [ ] Capability graph updated for merged EWO statuses

---

## Cross-slice wiring (wave-specific)

### Integration A

- [ ] `DecisionInspectorSection` imported into `ContextInspector`
- [ ] `ContextBar` receives `warningState` from decision hook
- [ ] Writing page loads context + editor without regression

### Integration B

- [ ] RightRail Contesto tab → ContextInspector
- [ ] RightRail Fonte tab → SourcePeekReader stub wired
- [ ] Session Continua URL params compatible with editor + context scope

### Integration C

- [ ] Review entry from Writing + Home functional
- [ ] Proposal queue → ReviewCompare data path verified

---

## Verdict

```text
[ ] PASS — authorize next wave dispatch
[ ] FAIL — corrective EWO or merge fix required
```

---

## WO-TRACE

```text
wave_{n} complete → PX2-INTEGRATION-{N} → wave_{n+1} authorized
```
