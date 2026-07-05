# Capability Resolver

Translate the object of the request into a node of a **Capability Graph**.
Reason on the graph, not on numbers.

## Which graph?

| Track | Graph | Program |
|-------|-------|---------|
| Runtime Platform (default) | `.asep/capabilities/runtime-platform.yaml` | plans/*.md |
| Thesis-agent migration, OR-*, E2E, Kimi migration | `.asep/capabilities/thesis-agent-migration.yaml` | `.asep/programs/thesis-agent-migration.yaml` |
| ThesisOS Product v2, PX-*, Sources, Knowledge | `.asep/capabilities/thesisos-product-v2.yaml` | `.asep/programs/thesisos-product-v2.yaml` |

**Load thesis-agent track** when the request mentions any of:
`thesis-agent`, `thesis agent`, `migration`, `kimi`, `OR-`, `operational readiness`,
`E2E`, `end-to-end`, `UNI-01`, `REL-01`, `engineering program`, `META-0`.

Before resolving capability on that track, read:
1. `docs/engineering-program.md` (outer/inner loop, lifecycle)
2. `.asep/programs/thesis-agent-migration.yaml` (backlog + completion criteria)

**Load thesisos-product track** when the request mentions any of:
`PX-1`…`PX-6`, `thesisos product`, `Sources`, `Knowledge`, `product v2`,
`AUTHORIZE PX`, or after `authorize` intent resolves to a PX milestone.

Before resolving on that track, read:
1. `.asep/programs/thesisos-product-v2.yaml`
2. `.asep/capabilities/thesisos-product-v2.yaml`
3. For conformance milestones (PX-3+): `.asep/governance/sor-compatibility-policy.md`

Otherwise load `runtime-platform.yaml` and the plan from `governance/manifest.yaml`.

## Steps

1. Select graph (see above) and load it.
2. Match request text against each node's `title`/`aliases` (case-insensitive).
   - "event bus" → `event-bus`; "qualifica il runtime" → `qualification`.
3. If no object is given, pick the first node with `status: ready` whose every
   `depends_on` is `done`.
4. From the node, read `phase`; open the matching section of `plan` for exact scope
   (the plan is authoritative).
5. **Prerequisite check** (all must pass, else STOP):
   - every `depends_on` capability is `status: done`
   - every `requires` ADR exists and is Accepted *(runtime track only)*
   - `baseline` (or graph's latest `done` baseline) == last commit on branch *(when baseline set)*
   - working tree clean *(for code-changing develop intent)*
   - `make ci` green on baseline *(runtime track code WO only)*
   - for OR/E2E: live stack reachable; Fase B promotion done (`phase-b-runtime-promotion`)
6. Emit a resolution summary, then proceed (or STOP):

```text
Capability: Runtime Platform / Event Bus  (phase M5.4B)
Prerequisites:
  ✓ event-contract (done @ 0339643)
  ✓ ADR-0030 accepted
  ✓ Runtime Constitution
  ✓ baseline == HEAD, tree clean
→ proceed
```

If any prerequisite is ✗, output it and STOP (no implementation).
