FROM python:3.12-slim
WORKDIR /app
# Docling's PDF pipeline pulls in native deps (via PyTorch/OpenCV) that expect X11
# shared libs even in headless containers. Without these, PDF conversion fails with
# libxcb.so.1 missing and the parser boundary falls back to PyMuPDF unconditionally.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 libglib2.0-0 libgl1 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*
# Install dependencies from metadata before copying application code so normal
# Python edits do not invalidate the expensive parser/ML dependency layer.
COPY backend/pyproject.toml ./
# Install the parser backends (Docling + PyMuPDF) so document ingestion works in
# the image — the runtime must not depend on packages installed by hand in the
# container (M4 recovery, bug-3). Preinstall the CPU wheel so pip does not pull
# the multi-gigabyte CUDA runtime into this CPU-only service.
RUN pip install --no-cache-dir \
      "torch==2.13.0+cpu" \
      --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir ".[parsers]"
# Copy and install the local package without resolving dependencies again.
COPY backend/ ./
RUN pip install --no-cache-dir --no-deps .
# The in-process event bus resolves the repo-root-relative event catalog here.
COPY contracts/ /contracts/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
