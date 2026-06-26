FROM python:3.12-slim
WORKDIR /app
# Docling's PDF pipeline pulls in native deps (via PyTorch/OpenCV) that expect X11
# shared libs even in headless containers. Without these, PDF conversion fails with
# libxcb.so.1 missing and the parser boundary falls back to PyMuPDF unconditionally.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 libglib2.0-0 libgl1 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*
# Binary wheels (psycopg[binary], uvicorn[standard]) avoid needing build toolchain; keep slim.
# Single COPY + install keeps layering simple and correct: setuptools package discovery
# (include=["app*"]) requires app code to be present at build time.
COPY backend/ ./
# The in-process event bus reads the event catalog at runtime and resolves it to
# /contracts/events/events.json inside the container (repo-root-relative path).
# It is a sibling of backend/, so it must be copied explicitly or every
# event-publishing flow (upload, ChunkCreated, …) fails with FileNotFoundError.
COPY contracts/ /contracts/
# Install the parser backends (Docling + PyMuPDF) so document ingestion works in
# the image — the runtime must not depend on packages installed by hand in the
# container (M4 recovery, bug-3). Docling is heavy (ML deps); the image is large.
RUN pip install --no-cache-dir ".[parsers]"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
