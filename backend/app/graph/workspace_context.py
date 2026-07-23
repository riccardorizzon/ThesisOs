"""Workspace + Companion preamble — experience target ≥9 (PM-008)."""

from __future__ import annotations

import logging
import re

from langchain_core.runnables import RunnableConfig

from app.graph.academic_production import last_user_content
from app.graph.companion.pillar import classify_pillar, is_affirmation
from app.graph.companion.protocol import (
    COMPANION_OPEN_UTTERANCE,
    is_companion_open,
)
from app.graph.companion.prompts import (
    COMPANION_SYSTEM,
    CONTINUE_CONFIRM_HINT,
    LEARNED_ACK_HINT,
    OPENING_09_00_HINT,
    PILLAR_HINT_TEMPLATE,
    PRESERVE_HINT,
    SAVE_HINT,
)
from app.graph.companion.review_state import REVIEW_PHASE_HINTS, infer_review_phase
from app.schemas.graph_state import GraphState, Message
from app.services.memory.service import MemoryService
from app.services.workspace.learning_loop import (
    is_learning_confirmation,
    load_pending_rule,
    process_learning_turn,
)
from app.services.workspace.render import render_workspace_empty, render_workspace_snapshot
from app.services.workspace.snapshot import WorkspaceLoader
from app.services.workspace.thesis_sor import THESIS_AGENT_PROJECT_ID

logger = logging.getLogger("app.graph.workspace_context")


def _conversation_turn_count(messages: list[Message]) -> int:
    return sum(1 for m in messages if m.role == "user" and m.content.strip())


def _last_assistant_content(messages: list[Message]) -> str | None:
    for m in reversed(messages):
        if m.role == "assistant" and (m.content or "").strip():
            return m.content
    return None


def _normalize_utterance(utterance: str | None) -> str | None:
    if is_companion_open(utterance):
        return COMPANION_OPEN_UTTERANCE
    return utterance


def make_workspace_context_node(
    loader: WorkspaceLoader | None = None,
    *,
    memory_service: MemoryService | None = None,
):
    svc = loader or WorkspaceLoader()

    async def workspace_context_node(state: GraphState, config: RunnableConfig) -> dict:
        configurable = config.get("configurable") or {}
        project_id = configurable.get("project_id")
        if project_id != THESIS_AGENT_PROJECT_ID:
            return {}
        raw_utterance = last_user_content(state.messages)
        utterance = _normalize_utterance(raw_utterance)
        prior_assistant = _last_assistant_content(state.messages)
        pillar = classify_pillar(utterance, prior_assistant=prior_assistant)

        snapshot = await svc.load(
            project_id=project_id,
            conversation_messages=_conversation_turn_count(state.messages),
        )
        workspace_text = render_workspace_snapshot(snapshot)
        if not workspace_text:
            workspace_text = render_workspace_empty()

        turns = _conversation_turn_count(state.messages)
        is_open = is_companion_open(raw_utterance) or (
            turns <= 1 and pillar == "CONTINUE"
        )

        prefix: list[Message] = [
            Message(role="system", content=COMPANION_SYSTEM),
            Message(
                role="system",
                content=PILLAR_HINT_TEMPLATE.format(pillar=pillar),
            ),
            Message(role="system", content=workspace_text),
        ]
        if is_open and pillar == "CONTINUE":
            prefix.append(Message(role="system", content=OPENING_09_00_HINT))
        elif pillar == "CONTINUE" and is_affirmation(utterance):
            prefix.append(Message(role="system", content=CONTINUE_CONFIRM_HINT))
        elif pillar == "CONTINUE" and re.search(
            r"\b(continuiamo|vai)\b", utterance or "", re.I
        ):
            prefix.append(Message(role="system", content=CONTINUE_CONFIRM_HINT))

        phase = infer_review_phase(
            pillar=pillar,
            utterance=utterance,
            prior_assistant=prior_assistant,
        )
        if phase:
            prefix.append(Message(role="system", content=REVIEW_PHASE_HINTS[phase]))

        if pillar == "PRESERVE":
            prefix.append(Message(role="system", content=PRESERVE_HINT))
        elif pillar == "SAVE":
            prefix.append(Message(role="system", content=SAVE_HINT))

        if project_id == THESIS_AGENT_PROJECT_ID and utterance:
            # Learning loop writes PERSISTENT_MEMORY (ADR-0046): failures are
            # logged and the turn continues without a learning hint — never
            # swallowed silently.
            try:
                mem = memory_service or MemoryService()
                pending_before = await load_pending_rule(mem)
                hint = await process_learning_turn(
                    mem,
                    user_text=raw_utterance or utterance,
                )
                if hint:
                    prefix.append(Message(role="system", content=hint))
                elif (
                    pending_before
                    and is_learning_confirmation(raw_utterance or utterance)
                ):
                    prefix.append(Message(role="system", content=LEARNED_ACK_HINT))
            except Exception:
                logger.exception(
                    "learning loop failed for project %s — continuing turn "
                    "without learning hint",
                    project_id,
                )

        return {"messages": [*prefix, *state.messages]}

    return workspace_context_node
