# Capability Resolver

Translate the object of the request into a node of the Capability Graph
(`.asep/capabilities/runtime-platform.yaml`). Reason on the graph, not on numbers.

## Steps

1. Load the capability graph.
2. Match request text against each node's `title`/`aliases` (case-insensitive).
   - "event bus" → `event-bus`; "qualifica il runtime" → `qualification`.
3. If no object is given, pick the first node with `status: ready` whose every
   `depends_on` is `done`.
4. From the node, read `phase`; open the matching section of `plan` for exact scope
   (the plan is authoritative).
5. **Prerequisite check** (all must pass, else STOP):
   - every `depends_on` capability is `status: done`
   - every `requires` ADR exists and is Accepted
   - `baseline` (or graph's latest `done` baseline) == last commit on branch
   - working tree clean
   - `make ci` green on baseline
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
