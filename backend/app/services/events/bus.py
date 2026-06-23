async def publish(event_name: str, payload: dict) -> None:
    """In-process stub (ADR-0006). Persistence + consumers wired later."""
    raise NotImplementedError("event bus wired post-M0")
