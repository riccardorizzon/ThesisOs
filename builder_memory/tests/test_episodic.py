import pytest

from builder_memory.episodic.store import EpisodicStore


def test_append_lesson_requires_refs(mini_repo):
    store = EpisodicStore(mini_repo)
    with pytest.raises(ValueError):
        store.append(entry_type="lesson_learned", summary="test")


def test_forbidden_type(mini_repo):
    store = EpisodicStore(mini_repo)
    with pytest.raises(ValueError, match="forbidden"):
        store.append(entry_type="contract_mutation", summary="bad")


def test_append_and_recent(mini_repo):
    store = EpisodicStore(mini_repo)
    entry = store.append(
        entry_type="task_outcome",
        summary="Packet P-B done",
        source_refs=["plans/builder/STATE.yaml"],
        packet_id="P-B",
    )
    recent = store.recent(limit=1)
    assert recent[0].id == entry.id
