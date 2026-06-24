import pytest
from app.services.conversation.locks import ConversationLocks


async def test_lock_rejects_second_active_run():
    locks = ConversationLocks()
    assert locks.try_acquire("c1") is True
    assert locks.try_acquire("c1") is False   # already active -> caller returns 409
    locks.release("c1")
    assert locks.try_acquire("c1") is True
