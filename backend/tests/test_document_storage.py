from app.services.document.storage import (
    LocalStorageAdapter,
    sanitize_filename,
    storage_key,
)


def test_sanitize_filename_strips_paths_and_unsafe_chars():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename(None) == "file"
    assert sanitize_filename("") == "file"
    cleaned = sanitize_filename("My File (1).pdf")
    assert " " not in cleaned and "/" not in cleaned
    assert cleaned.endswith(".pdf")


def test_storage_key_layout():
    assert storage_key("doc-1", "a b.pdf") == "documents/doc-1/original/a_b.pdf"


def test_local_adapter_roundtrip(tmp_path):
    adapter = LocalStorageAdapter(tmp_path)
    key = storage_key("d1", "f.pdf")
    uri = adapter.put(key, b"hello")
    assert uri == f"local://{key}"
    assert adapter.get(key) == b"hello"
    adapter.delete(key)
    adapter.delete(key)  # idempotent — no error when already gone
