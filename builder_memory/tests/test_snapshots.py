from builder_memory.snapshots.snapshot import SnapshotStore, diff_since_snapshot


def test_snapshot_and_diff(mini_repo):
    store = SnapshotStore(mini_repo)
    snap = store.create("m1-complete")
    assert snap.milestone == "m1-complete"
    assert len(snap.files) >= 3

    changed = diff_since_snapshot(mini_repo, snap)
    assert changed == []

    # Modify a file.
    path = mini_repo / "knowledge/context/current-state.md"
    path.write_text("# Changed\n", encoding="utf-8")
    changed = diff_since_snapshot(mini_repo, snap)
    assert "knowledge/context/current-state.md" in changed
