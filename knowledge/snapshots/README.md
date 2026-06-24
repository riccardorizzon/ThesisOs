# Knowledge Snapshots

Milestone closure manifests for Builder Memory change detection (ADR-0019).

Each snapshot records **file hashes** of the indexed corpus at a milestone tag.
Builder Memory uses these to report what changed since the last gate without
re-reading the entire repository.

## Create at milestone closure

```bash
builder-memory snapshot --milestone m1-complete
```

## Files

| Snapshot | Milestone |
|----------|-----------|
| `m1-complete.json` | M1 Conversation System |

Snapshots are **git-tracked**. The BM25 index (`.builder-memory/`) is **not**.
