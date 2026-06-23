FROM python:3.12-slim
WORKDIR /app
# Binary wheels (psycopg[binary], uvicorn[standard]) avoid needing build toolchain; keep slim.
# Single COPY + install keeps layering simple and correct: setuptools package discovery
# (include=["app*"]) requires app code to be present at build time.
COPY backend/ ./
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
