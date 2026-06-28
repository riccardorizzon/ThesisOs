# Capabilities

`runtime-platform.yaml` is the **Capability Graph** the ASEP skill reasons over.

The skill resolves a request to a capability node, not a milestone number, then
checks the node's prerequisites (`depends_on` done, `requires` ADRs present,
`baseline` = last commit) before executing.

The **plan** (`plans/*.md`) stays authoritative for exact scope; this graph is the
navigation layer. Keep `status` and `baseline` fields in sync after each milestone.
