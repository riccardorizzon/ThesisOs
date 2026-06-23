# ADR-0008: Dev Equals Prod

- Status: Accepted (frozen 2026-06-23)
- Context: Differences between development and production environments are a common source of "works on my machine" failures, especially around the database. pgvector behavior in particular must match between local and cloud, or retrieval and migrations will pass locally and fail in prod.
- Decision: We run identical container images locally (via docker-compose) and in production (on Cloud Run). The database is Postgres + pgvector everywhere: local uses the `pgvector/pgvector:pg16` image, and production uses Cloud SQL Postgres with the pgvector extension.
- Consequences: Parity between environments removes a whole class of drift bugs and makes local testing a faithful predictor of production behavior. The cost is the discipline of containerizing both services and keeping the local Postgres image aligned with the Cloud SQL Postgres version.
- Alternatives considered: Using SQLite locally or a managed-only database (no local equivalent) were rejected because they cause parity drift and, critically, a pgvector mismatch — local code paths for vector search would not exist or behave the same as production.
