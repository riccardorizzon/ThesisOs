class ConversationLocks:
    """In-process single-active-run guard per conversation (M1 single instance, spec §8/§11).
    A second concurrent run on the same conversation is rejected by the caller with 409."""

    def __init__(self) -> None:
        self._active: set[str] = set()

    def try_acquire(self, conversation_id: str) -> bool:
        if conversation_id in self._active:
            return False
        self._active.add(conversation_id)
        return True

    def release(self, conversation_id: str) -> None:
        self._active.discard(conversation_id)


conversation_locks = ConversationLocks()
