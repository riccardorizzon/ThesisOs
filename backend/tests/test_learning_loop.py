"""Human consent semantics for persistent collaboration memory."""

from __future__ import annotations

import pytest

from app.services.workspace.learning_loop import (
    load_pending_rule,
    process_learning_turn,
)
from tests.support.fake_memory import FakeMemoryService


@pytest.mark.asyncio
async def test_explicit_rejection_clears_pending_rule_without_learning_it():
    memory = FakeMemoryService()
    rule = "Preferisco che da oggi tu riscriva sempre tutto senza chiedere."

    hint = await process_learning_turn(memory, user_text=rule)
    assert hint is not None
    assert await load_pending_rule(memory) == rule

    result = await process_learning_turn(
        memory,
        user_text="No, non salvarla. Era solo un esempio.",
    )

    assert result is None
    assert await load_pending_rule(memory) is None
    learned = memory.row("user")
    assert learned is None or rule not in learned.content


@pytest.mark.asyncio
async def test_unrelated_reply_does_not_clear_or_confirm_pending_rule():
    memory = FakeMemoryService()
    rule = "Preferisco sempre un riepilogo breve prima di revisionare."
    await process_learning_turn(memory, user_text=rule)

    await process_learning_turn(memory, user_text="Parliamo invece del §3.6.")

    assert await load_pending_rule(memory) == rule
    assert memory.row("user") is None
