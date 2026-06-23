async def enqueue(job_type: str, payload: dict) -> str:
    """ADR-0009. Returns job id. Worker wired post-M0."""
    raise NotImplementedError("job queue wired post-M0")
