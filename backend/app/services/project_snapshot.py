from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectSnapshotNotFoundError(LookupError):
    pass


_PROJECT_QUERIES: dict[str, str] = {
    "project": "SELECT * FROM projects WHERE id = :pid",
    "documents": "SELECT * FROM documents WHERE project_id = :pid",
    "document_versions": """
        SELECT version.*
        FROM document_versions version
        JOIN documents document ON document.id = version.document_id
        WHERE document.project_id = :pid
    """,
    "chunks": """
        SELECT chunk.*
        FROM chunks chunk
        JOIN documents document ON document.id = chunk.document_id
        WHERE document.project_id = :pid
    """,
    "embeddings": """
        SELECT embedding.id, embedding.owner_type, embedding.owner_id,
               embedding.model, embedding.dimension, embedding.metadata,
               embedding.content_hash, embedding.created_at
        FROM embeddings embedding
        JOIN chunks chunk ON chunk.id = embedding.owner_id
        JOIN documents document ON document.id = chunk.document_id
        WHERE embedding.owner_type = 'chunk'
          AND document.project_id = :pid
    """,
    "sources": "SELECT * FROM sources WHERE project_id = :pid",
    "chapters": "SELECT * FROM chapters WHERE project_id = :pid",
    "chapter_versions": """
        SELECT version.*
        FROM chapter_versions version
        JOIN chapters chapter ON chapter.id = version.chapter_id
        WHERE chapter.project_id = :pid
    """,
    "citations": """
        SELECT citation.*
        FROM citations citation
        WHERE citation.chapter_id IN (
          SELECT id FROM chapters WHERE project_id = :pid
        )
        OR citation.source_id IN (
          SELECT id FROM sources WHERE project_id = :pid
        )
    """,
    "notes": "SELECT * FROM notes WHERE project_id = :pid",
    "memories": "SELECT * FROM memories WHERE project_id = :pid",
    "memory_versions": """
        SELECT version.*
        FROM memory_versions version
        JOIN memories memory ON memory.id = version.memory_id
        WHERE memory.project_id = :pid
    """,
    "conversations": "SELECT * FROM conversations WHERE project_id = :pid",
    "messages": """
        SELECT message.*
        FROM messages message
        JOIN conversations conversation
          ON conversation.id = message.conversation_id
        WHERE conversation.project_id = :pid
    """,
    "agent_runs": "SELECT * FROM agent_runs WHERE project_id = :pid",
    "agent_steps": """
        SELECT step.*
        FROM agent_steps step
        JOIN agent_runs run ON run.id = step.agent_run_id
        WHERE run.project_id = :pid
    """,
    "proposals": "SELECT * FROM proposals WHERE project_id = :pid",
    "tasks": "SELECT * FROM tasks WHERE project_id = :pid",
    "events": "SELECT * FROM events WHERE project_id = :pid",
    "concepts": "SELECT * FROM concepts WHERE project_id = :pid",
    "concept_source_links": """
        SELECT link.*
        FROM concept_source_links link
        WHERE link.concept_id IN (
          SELECT id FROM concepts WHERE project_id = :pid
        )
        OR link.source_slug IN (
          SELECT slug FROM sources WHERE project_id = :pid
        )
    """,
    "concept_relations": """
        SELECT relation.*
        FROM concept_relations relation
        WHERE relation.from_concept_id IN (
          SELECT id FROM concepts WHERE project_id = :pid
        )
        OR relation.to_concept_id IN (
          SELECT id FROM concepts WHERE project_id = :pid
        )
    """,
}


def _canonical_value(value):
    if isinstance(value, dict):
        return {
            str(key): _canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    return value


def _canonical_json(value) -> str:
    return json.dumps(
        _canonical_value(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def _digest(value) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


async def snapshot_project(
    session: AsyncSession,
    project_id: str,
) -> dict:
    project_exists = (
        await session.execute(
            text("SELECT 1 FROM projects WHERE id = :pid"),
            {"pid": project_id},
        )
    ).scalar_one_or_none()
    if project_exists is None:
        raise ProjectSnapshotNotFoundError(project_id)

    aggregates: dict[str, dict[str, int | str]] = {}
    for name, query in _PROJECT_QUERIES.items():
        result = await session.execute(text(query), {"pid": project_id})
        rows = [_canonical_value(dict(row)) for row in result.mappings().all()]
        rows.sort(key=_canonical_json)
        aggregates[name] = {
            "count": len(rows),
            "sha256": _digest(rows),
        }

    return {
        "schema_version": "1",
        "project_id": project_id,
        "aggregates": aggregates,
        "overall_sha256": _digest(aggregates),
    }
