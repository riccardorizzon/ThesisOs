#!/usr/bin/env python3
"""Promote knowledge/thesis-agent blueprint into ThesisOS runtime (migration Phase B).

Uses the live ThesisOS HTTP API (default http://localhost:8000). Idempotent:
skips documents/chapters already tagged with migration_run=kimi-claw-2026-06.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("httpx required: pip install httpx", file=sys.stderr)
    sys.exit(1)

MIGRATION_RUN = "kimi-claw-2026-06"
MIGRATION_TAG = f"[{MIGRATION_RUN}]"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def agent_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :].lstrip("\n")
    return text


def section(title: str, body: str) -> str:
    return f"\n\n---\n\n## {title}\n\n{body.strip()}\n"


class Promoter:
    def __init__(self, base_url: str, dry_run: bool = False):
        self.base = base_url.rstrip("/")
        self.dry_run = dry_run
        self.client = httpx.Client(base_url=self.base, timeout=120.0)
        self.log: list[str] = []

    def note(self, msg: str) -> None:
        self.log.append(msg)
        print(msg)

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        if self.dry_run:
            raise RuntimeError("dry-run")
        return self.client.get(path, params=params)

    def _post(self, path: str, **kwargs) -> httpx.Response:
        if self.dry_run:
            raise RuntimeError("dry-run")
        return self.client.post(path, **kwargs)

    def _patch(self, path: str, **kwargs) -> httpx.Response:
        if self.dry_run:
            raise RuntimeError("dry-run")
        return self.client.patch(path, **kwargs)

    def list_memories(self, kind: str | None = None) -> list[dict]:
        params = {"limit": 200}
        if kind:
            params["kind"] = kind
        r = self._get("/memory", params=params)
        r.raise_for_status()
        return r.json()

    def upsert_memory(
        self,
        *,
        kind: str,
        content: str,
        title: str | None = None,
        key: str | None = None,
        source: str = "migration",
    ) -> None:
        existing = None
        for row in self.list_memories(kind=kind):
            if key is not None and row.get("key") == key:
                existing = row
                break
            if key is None and kind in {"editable", "thesis", "user"}:
                if row.get("key") == kind or (kind == "editable" and row.get("kind") == "editable"):
                    existing = row
                    break
        if existing:
            self.note(f"  memory UPDATE kind={kind} key={key or existing.get('key')} id={existing['id']}")
            if not self.dry_run:
                r = self._patch(
                    f"/memory/{existing['id']}",
                    json={
                        "title": title,
                        "content": content,
                        "expected_version": existing["version"],
                    },
                )
                r.raise_for_status()
        else:
            self.note(f"  memory CREATE kind={kind} key={key} title={title!r}")
            if not self.dry_run:
                body = {"kind": kind, "content": content, "title": title, "source": source}
                if key:
                    body["key"] = key
                r = self._post("/memory", json=body)
                if r.status_code == 409 and kind == "editable":
                    # singleton race — retry as update
                    return self.upsert_memory(
                        kind=kind, content=content, title=title, key=key, source=source
                    )
                r.raise_for_status()

    def build_editable(self, root: Path) -> str:
        parts = [
            "# Thesis Agent — operational rules (promoted from knowledge/thesis-agent)\n",
            f"Migration run: {MIGRATION_RUN}. Persona chat-only excluded (see Conversation.md).\n",
        ]
        files = [
            ("01_SYSTEM/Identity.md", "Identità"),
            ("01_SYSTEM/Behaviour.md", "Comportamento"),
            ("01_SYSTEM/Conversation.md", "Conversazione vs scrittura"),
            ("01_SYSTEM/Memory-Protocol.md", "Protocollo memoria"),
            ("02_METHOD/Research-Protocol.md", "Ricerca"),
            ("02_METHOD/Review-Protocol.md", "Revisione"),
            ("02_METHOD/Revision-Workflow.md", "Workflow revisione"),
            ("02_METHOD/Source-Classification.md", "Classificazione fonti"),
            ("02_METHOD/Writing-Rules.md", "Regole scrittura"),
            ("03_PROJECT/University-Rules.md", "Regole università (UNI-01)"),
            ("03_PROJECT/Relatrice-Rules.md", "Regole relatrice (REL-01)"),
            ("03_PROJECT/Project-Rules.md", "Regole progetto"),
            ("05_MEMORY/Permanent.md", "Memoria permanente"),
        ]
        for rel, heading in files:
            path = root / rel
            if path.exists():
                parts.append(section(heading, read_md(path)))
        return "".join(parts)

    def promote_memories(self, root: Path) -> None:
        self.note("=== Memories (M2) ===")
        editable = self.build_editable(root)
        self.upsert_memory(
            kind="editable",
            key="editable",
            title="Thesis agent rules",
            content=editable,
        )
        thesis_path = root / "03_PROJECT/Thesis-State.md"
        self.upsert_memory(
            kind="thesis",
            key="thesis",
            title="Thesis state",
            content=read_md(thesis_path),
        )
        decision_files = [
            ("decisions", "03_PROJECT/Decisions.md", "Project decisions"),
            ("university-rules", "03_PROJECT/University-Rules.md", "University rules UNI-01"),
            ("relatrice-rules", "03_PROJECT/Relatrice-Rules.md", "Relatrice rules REL-01"),
        ]
        for key, rel, title in decision_files:
            path = root / rel
            if path.exists():
                self.upsert_memory(
                    kind="decision",
                    key=key,
                    title=title,
                    content=read_md(path),
                )

    def list_documents(self) -> list[dict]:
        r = self._get("/documents", params={"limit": 200})
        r.raise_for_status()
        return r.json()

    def document_exists(self, filename: str) -> bool:
        for doc in self.list_documents():
            if doc.get("original_filename") == filename:
                return True
            title = doc.get("title") or ""
            if MIGRATION_TAG in title and filename in title:
                return True
        return False

    def wait_document(self, doc_id: str, timeout: float = 300.0) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = self._get(f"/documents/{doc_id}")
            r.raise_for_status()
            doc = r.json()
            status = doc.get("status")
            if status in {"parsed", "indexed", "failed"}:
                return doc
            time.sleep(2)
        raise TimeoutError(f"document {doc_id} not terminal after {timeout}s")

    def upload_document(self, path: Path, *, title: str, author: str | None = None) -> dict | None:
        filename = path.name
        if self.document_exists(filename):
            self.note(f"  document SKIP (exists) {filename}")
            return None
        tagged_title = f"{MIGRATION_TAG} {title}"
        self.note(f"  document UPLOAD {filename} → {tagged_title!r}")
        if self.dry_run:
            return None
        with path.open("rb") as fh:
            r = self._post(
                "/upload",
                files={"file": (filename, fh, "application/octet-stream")},
                data={"title": tagged_title, "author": author or ""},
            )
        r.raise_for_status()
        doc = r.json()
        doc = self.wait_document(doc["id"])
        self.note(f"    → status={doc['status']} chunks={doc.get('chunk_count')}")
        return doc

    def promote_documents(self, root: Path) -> None:
        self.note("=== Documents (M3/M4) ===")
        patterns = [
            (root / "04_KNOWLEDGE" / "Books" / "*.md", "book"),
            (root / "04_KNOWLEDGE" / "University" / "*.md", "university"),
            (root / "04_KNOWLEDGE" / "Bibliography" / "*.md", "bibliography"),
            (root / "04_KNOWLEDGE" / "References" / "*.md", "reference"),
            (root / "04_KNOWLEDGE" / "Relatrice" / "transcription" / "page_*.md", "relatrice"),
        ]
        for pattern, category in patterns:
            for path in sorted(pattern.parent.glob(pattern.name)):
                if path.name in {"README.md", "VALIDATION.md"}:
                    continue
                author = category
                title = path.stem.replace("_", " ")
                self.upload_document(path, title=title, author=author)
        pdf = root / "04_KNOWLEDGE" / "Relatrice" / "prima-revisione-2026-05-27.pdf"
        if pdf.exists():
            self.upload_document(pdf, title="Prima revisione relatrice 2026-05-27", author="relatrice")

    def list_chapters(self) -> list[dict]:
        r = self._get("/chapters", params={"limit": 200})
        r.raise_for_status()
        return r.json()

    def chapter_exists(self, slug: str) -> bool:
        for ch in self.list_chapters():
            md = ch.get("content_md") or ""
            if f"migration_slug:{slug}" in md[:200]:
                return True
            if slug in (ch.get("title") or ""):
                return True
        return False

    def promote_chapters(self, root: Path) -> None:
        self.note("=== Chapters (M6) ===")
        chapter_specs = [
            ("ch01/1.1_Il_processo_creativo_come_processo_di_soluzione_di_problemi.md", 0, "§1.1 Il processo creativo come soluzione di problemi"),
            ("ch01/1.2_La_dimensione_psicologica_flow_e_coinvolgimento.md", 1, "§1.2 La dimensione psicologica: flow e coinvolgimento"),
            ("ch01/1.3_Il_processo_creativo_nel_fashion_design_una_sintesi.md", 2, "§1.3 Il processo creativo nel fashion design: sintesi"),
            ("ch02/2.1_La_ricerca_come_fase_fondamentale.md", 3, "§2.1 La ricerca come fase fondamentale"),
            ("ch02/2.2_Il_moodboard_come_dispositivo_di_memoria.md", 4, "§2.2 Il moodboard come dispositivo di memoria"),
            ("ch02/2.3_Aura_riproduzione_e_trasformazione_del_riferimento.md", 5, "§2.3 Aura, riproduzione e trasformazione del riferimento"),
            ("ch02/2.4_Sintesi_metodologica_le_tre_prospettive.md", 6, "§2.4 Sintesi metodologica: le tre prospettive"),
            ("ch03/CAP03_progettazione_metodologica.md", 7, "Cap. 3 — Progettazione metodologica"),
        ]
        for rel, order_index, title in chapter_specs:
            path = root / "chapters" / rel
            slug = rel.replace("/", "-")
            if not path.exists():
                self.note(f"  chapter MISSING {rel}")
                continue
            if self.chapter_exists(slug):
                self.note(f"  chapter SKIP (exists) {title}")
                continue
            body = read_md(path)
            content = f"<!-- migration_slug:{slug} migration_run:{MIGRATION_RUN} -->\n\n{body}"
            self.note(f"  chapter CREATE {title}")
            if not self.dry_run:
                r = self._post(
                    "/chapters",
                    json={
                        "title": f"{MIGRATION_TAG} {title}",
                        "order_index": order_index,
                        "status": "review",
                        "content_md": content,
                    },
                )
                r.raise_for_status()

    def run(self, root: Path) -> None:
        self.promote_memories(root)
        self.promote_documents(root)
        self.promote_chapters(root)


def write_log(log_path: Path, lines: list[str]) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    header = f"\n## Promozione runtime — {ts}\n\n"
    body = "\n".join(f"- {line}" for line in lines)
    if log_path.exists():
        log_path.write_text(log_path.read_text(encoding="utf-8") + header + body + "\n", encoding="utf-8")
    else:
        log_path.write_text(f"# Promotion log\n{header}{body}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = agent_root()
    promoter = Promoter(args.base_url, dry_run=args.dry_run)
    try:
        promoter.run(root)
    except httpx.HTTPError as exc:
        promoter.note(f"ERROR: {exc}")
        write_log(root / "_migration" / "promotion-log.md", promoter.log)
        return 1
    write_log(root / "_migration" / "promotion-log.md", promoter.log)
    promoter.note("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
