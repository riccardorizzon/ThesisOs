class MemoryServiceError(Exception):
    """Base error for MemoryService domain failures."""


class WriteConflictError(MemoryServiceError):
    """Optimistic lock failure — maps to memory_ops.write_conflict (M5+)."""

    def __init__(self, memory_id: str, *, expected_version: int, actual_version: int):
        self.memory_id = memory_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"write_conflict: memory {memory_id} expected version {expected_version}, "
            f"actual {actual_version}"
        )


class SingletonMemoryExistsError(MemoryServiceError):
    """Second create for a singleton operational kind."""

    def __init__(self, kind: str, key: str):
        self.kind = kind
        self.key = key
        super().__init__(f"singleton memory already exists: kind={kind} key={key}")


class CannotDeleteSingletonError(MemoryServiceError):
    """Singleton operational memories cannot be deleted."""

    def __init__(self, kind: str):
        self.kind = kind
        super().__init__(f"cannot delete singleton memory kind={kind}")


class MemoryNotFoundError(MemoryServiceError):
    def __init__(self, memory_id: str):
        self.memory_id = memory_id
        super().__init__(f"memory not found: {memory_id}")
