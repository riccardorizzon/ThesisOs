"""Original-bytes storage boundary (M3, spec §4.1).

Two adapters behind one Protocol: a local filesystem adapter for dev/tests and a
GCS adapter for cloud. Object key layout is identical across both:
``documents/{document_id}/original/{sanitized_filename}``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol, runtime_checkable

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_filename(name: str | None) -> str:
    """Strip path components and unsafe chars from an uploaded filename."""
    base = (name or "file").replace("\\", "/").split("/")[-1]
    cleaned = _SAFE_CHARS.sub("_", base).strip("_")
    return cleaned or "file"


def storage_key(document_id: str, filename: str | None) -> str:
    """Deterministic object key for a document's original bytes."""
    return f"documents/{document_id}/original/{sanitize_filename(filename)}"


@runtime_checkable
class StorageAdapter(Protocol):
    def put(self, key: str, data: bytes) -> str: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def uri(self, key: str) -> str: ...


class LocalStorageAdapter:
    """Filesystem adapter mirroring the GCS key layout (env ``local``)."""

    def __init__(self, base_dir: str | Path):
        self.base = Path(base_dir)

    def _path(self, key: str) -> Path:
        return self.base / key

    def put(self, key: str, data: bytes) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return self.uri(key)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def uri(self, key: str) -> str:
        return f"local://{key}"


class GCSStorageAdapter:
    """Google Cloud Storage adapter. The client is imported + built lazily so the
    package imports without ``google-cloud-storage`` present (e.g. in CI)."""

    def __init__(self, bucket: str):
        self.bucket_name = bucket
        self._client = None

    def _bucket(self):
        if self._client is None:
            from google.cloud import storage  # lazy import

            self._client = storage.Client()
        return self._client.bucket(self.bucket_name)

    def put(self, key: str, data: bytes) -> str:
        self._bucket().blob(key).upload_from_string(data)
        return self.uri(key)

    def get(self, key: str) -> bytes:
        return self._bucket().blob(key).download_as_bytes()

    def delete(self, key: str) -> None:
        blob = self._bucket().blob(key)
        if blob.exists():
            blob.delete()

    def uri(self, key: str) -> str:
        return f"gs://{self.bucket_name}/{key}"


def build_storage_adapter() -> StorageAdapter:
    """Construct the configured adapter from settings (`DOCUMENT_STORAGE_BACKEND`)."""
    from app.core.config import settings

    backend = (settings.document_storage_backend or "local").lower()
    if backend == "gcs":
        return GCSStorageAdapter(settings.documents_bucket)
    return LocalStorageAdapter(settings.document_storage_local_dir)
