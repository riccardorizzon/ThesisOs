"""Writer brief + draft result (M6, ADR-0031).

`DraftResult` is the **pure** output of a `WriterCapability` — isolated from
`ChapterService`, REST, DB, and the Event Bus (ADR-0031 §3). A separate layer
decides what to do with it (save / show / discard / compare). The writer node
adapts a `DraftResult` into the frozen `GraphState` partial (`draft`, `citations`).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.graph_state import CitationRef, Message, Plan, RetrievedChunk


class WriterBrief(BaseModel):
    """Pure input to a `WriterCapability`, assembled from frozen GraphState."""

    plan: Plan | None = None
    retrieved_context: list[RetrievedChunk] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)


class DraftResult(BaseModel):
    """Pure output of `WriterCapability.write_grounded` (ADR-0031 §3).

    Only `draft` + `citations` map to GraphState (contracts/agents/writer.json);
    `metadata`, `reasoning`, and `metrics` ride the stream / Event Bus and are
    never written to the frozen GraphState (ADR-0007).
    """

    draft: str
    citations: list[CitationRef] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    reasoning: str | None = None
    metrics: dict = Field(default_factory=dict)
