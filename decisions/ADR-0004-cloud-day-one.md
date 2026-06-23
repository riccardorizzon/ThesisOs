# ADR-0004: Cloud Day One

- Status: Accepted (frozen 2026-06-23)
- Context: Deferring cloud deployment until late in the build invites infrastructure surprises — IAM, networking, Cloud SQL, secrets, and image delivery problems all surface at once when they are hardest to debug. ThesisOS targets GCP, so the environment should exist and be exercised from the very first milestone.
- Decision: We provision GCP from the start via Terraform: Cloud Run, Cloud SQL on `db-f1-micro`, Cloud Storage, Secret Manager, and Artifact Registry, with the required APIs enabled and a Cloud Run service account scoped to Vertex AI User, Cloud SQL Client, and Storage access.
- Consequences: We accept a small always-on Cloud SQL cost in exchange for eliminating dev≠prod drift and discovering infrastructure issues early, when they are cheap to fix. `db-f1-micro` is the cheapest shared-core tier and is intentionally not optimized yet.
- Alternatives considered: Local-first then deploy at M11 was rejected because it concentrates infrastructure risk into a late, high-pressure milestone. A single `e2-small` VM running docker-compose is documented as a cheaper fallback but was not chosen, because it diverges from the managed Cloud Run/Cloud SQL target.
