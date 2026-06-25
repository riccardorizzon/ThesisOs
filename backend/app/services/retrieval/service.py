"""RetrievalService — sole writer for chunk embeddings (ADR-0024)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import models
from app.db.models import EMBEDDING_DIM
from app.db.session_async import AsyncSessionLocal
from app.llm.base import LLMClient
from app.llm.factory import get_llm_client
from app.schemas.retrieval import SearchFilters, SearchResultItem
from app.services.document.exceptions import DocumentNotFoundError
from app.services.document.service import DocumentService
from app.services.retrieval.exceptions import EmbedFailedError, RetrievalServiceError


@dataclass(frozen=True)
class _ChunkRow:
    id: str
    document_id: str
    chunk_hash: str
    content: str


class RetrievalService:
    """Embed chunks and run hybrid search — reads documents/chunks read-only."""

    def __init__(
        self,
        *,
        llm: LLMClient | None = None,
        documents: DocumentService | None = None,
        embedding_model: str | None = None,
    ):
        self._llm = llm or get_llm_client()
        self._documents = documents or DocumentService()
        self._embedding_model = embedding_model or settings.embedding_model

    async def embed_document(
        self, document_id: str, *, session: AsyncSession | None = None
    ) -> int:
        """Embed all chunks for a parsed document; mark indexed on success."""
        if session is not None:
            return await self._embed_document(session, document_id)
        async with AsyncSessionLocal() as s:
            try:
                count = await self._embed_document(s, document_id)
                await s.commit()
                return count
            except Exception:
                await s.rollback()
                raise

    async def embed_chunks(
        self, chunk_ids: list[str], *, session: AsyncSession | None = None
    ) -> int:
        if session is not None:
            return await self._embed_chunks(session, chunk_ids)
        async with AsyncSessionLocal() as s:
            try:
                count = await self._embed_chunks(s, chunk_ids)
                await s.commit()
                return count
            except Exception:
                await s.rollback()
                raise

    async def delete_embeddings_for_document(
        self, document_id: str, *, session: AsyncSession
    ) -> None:
        chunk_ids = (
            await session.execute(
                select(models.Chunk.id).where(models.Chunk.document_id == document_id)
            )
        ).scalars().all()
        if not chunk_ids:
            return
        await session.execute(
            delete(models.Embedding).where(
                models.Embedding.owner_type == "chunk",
                models.Embedding.owner_id.in_(chunk_ids),
            )
        )

    async def search(
        self,
        query: str,
        *,
        filters: SearchFilters | None = None,
        limit: int = 10,
        hybrid_alpha: float = 0.5,
        session: AsyncSession | None = None,
    ) -> tuple[list[SearchResultItem], str]:
        if session is not None:
            return await self._search(session, query, filters, limit, hybrid_alpha)
        async with AsyncSessionLocal() as s:
            return await self._search(s, query, filters, limit, hybrid_alpha)

    async def _embed_document(self, session: AsyncSession, document_id: str) -> int:
        row = await session.get(models.Document, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        if row.status not in ("parsed", "indexed"):
            raise RetrievalServiceError(
                f"document {document_id} must be parsed before indexing (status={row.status})"
            )

        chunks = (
            await session.execute(
                select(models.Chunk).where(models.Chunk.document_id == document_id)
            )
        ).scalars().all()
        if not chunks:
            raise RetrievalServiceError(f"document {document_id} has no chunks to embed")

        embedded = await self._embed_chunk_rows(
            session,
            [
                _ChunkRow(id=c.id, document_id=c.document_id, chunk_hash=c.chunk_hash, content=c.content)
                for c in chunks
            ],
        )
        await self._documents.mark_indexed(document_id, session=session)
        return embedded

    async def _embed_chunks(self, session: AsyncSession, chunk_ids: list[str]) -> int:
        if not chunk_ids:
            return 0
        rows = (
            await session.execute(select(models.Chunk).where(models.Chunk.id.in_(chunk_ids)))
        ).scalars().all()
        return await self._embed_chunk_rows(
            session,
            [
                _ChunkRow(id=c.id, document_id=c.document_id, chunk_hash=c.chunk_hash, content=c.content)
                for c in rows
            ],
        )

    async def _embed_chunk_rows(
        self, session: AsyncSession, chunks: list[_ChunkRow]
    ) -> int:
        if not chunks:
            return 0

        to_embed: list[_ChunkRow] = []
        for chunk in chunks:
            existing = await session.execute(
                select(models.Embedding.id).where(
                    models.Embedding.owner_type == "chunk",
                    models.Embedding.owner_id == chunk.id,
                    models.Embedding.model == self._embedding_model,
                    models.Embedding.content_hash == chunk.chunk_hash,
                )
            )
            if existing.scalar_one_or_none() is None:
                to_embed.append(chunk)

        if not to_embed:
            return 0

        try:
            vectors = await self._llm.embed(
                [c.content for c in to_embed], model=self._embedding_model
            )
        except NotImplementedError as exc:
            raise EmbedFailedError(str(exc)) from exc
        except Exception as exc:
            raise EmbedFailedError(str(exc)) from exc

        if len(vectors) != len(to_embed):
            raise EmbedFailedError("embedding provider returned unexpected vector count")

        for chunk, vector in zip(to_embed, vectors, strict=True):
            if len(vector) != EMBEDDING_DIM:
                raise EmbedFailedError(
                    f"expected dimension {EMBEDDING_DIM}, got {len(vector)}"
                )
            session.add(
                models.Embedding(
                    owner_type="chunk",
                    owner_id=chunk.id,
                    model=self._embedding_model,
                    dimension=len(vector),
                    embedding=vector,
                    content_hash=chunk.chunk_hash,
                )
            )
        await session.flush()
        return len(to_embed)

    async def _search(
        self,
        session: AsyncSession,
        query: str,
        filters: SearchFilters | None,
        limit: int,
        hybrid_alpha: float,
    ) -> tuple[list[SearchResultItem], str]:
        filters = filters or SearchFilters()
        try:
            query_vectors = await self._llm.embed([query], model=self._embedding_model)
        except NotImplementedError as exc:
            raise EmbedFailedError(str(exc)) from exc
        except Exception as exc:
            raise EmbedFailedError(str(exc)) from exc

        if not query_vectors or len(query_vectors[0]) != EMBEDDING_DIM:
            raise EmbedFailedError("query embedding failed")

        query_vec = query_vectors[0]
        vec_literal = "[" + ",".join(str(v) for v in query_vec) + "]"

        clauses = ["d.status = 'indexed'", "e.model = :model"]
        params: dict = {
            "model": self._embedding_model,
            "query": query,
            "query_vec": vec_literal,
            "alpha": hybrid_alpha,
            "limit": limit,
        }
        if filters.document_ids:
            clauses.append("c.document_id = ANY(:document_ids)")
            params["document_ids"] = filters.document_ids
        if filters.source_types:
            clauses.append("d.source_type = ANY(:source_types)")
            params["source_types"] = filters.source_types

        where_sql = " AND ".join(clauses)
        stmt = text(
            f"""
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.chunk_hash,
                c.content,
                d.title AS document_title,
                c.page_from,
                c.page_to,
                (
                    :alpha * (1 - (e.embedding <=> CAST(:query_vec AS vector)))
                    + (1 - :alpha) * ts_rank(
                        c.content_tsv,
                        plainto_tsquery('english', :query)
                    )
                ) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            JOIN embeddings e
              ON e.owner_type = 'chunk'
             AND e.owner_id = c.id
             AND e.model = :model
            WHERE {where_sql}
            ORDER BY score DESC
            LIMIT :limit
            """
        )
        rows = (await session.execute(stmt, params)).mappings().all()
        results = [
            SearchResultItem(
                chunk_id=str(row["chunk_id"]),
                document_id=str(row["document_id"]),
                chunk_hash=row["chunk_hash"],
                score=float(row["score"] or 0.0),
                content=row["content"],
                document_title=row["document_title"],
                page_from=row["page_from"],
                page_to=row["page_to"],
            )
            for row in rows
        ]
        return results, self._embedding_model
