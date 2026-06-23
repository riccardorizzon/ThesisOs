resource "google_sql_database_instance" "pg" {
  name             = "thesisos-pg"
  database_version = "POSTGRES_16"
  region           = var.region

  # Single-user app: allow `terraform destroy` to remove the instance cleanly.
  deletion_protection = false

  settings {
    tier = var.db_tier
  }

  depends_on = [google_project_service.services]
}

resource "google_sql_database" "db" {
  name     = "thesisos"
  instance = google_sql_database_instance.pg.name
}

# The real password is supplied via Secret Manager / tfvars (see var.db_password
# in variables.tf); it is never committed to the repo.
resource "google_sql_user" "user" {
  name     = "thesisos"
  instance = google_sql_database_instance.pg.name
  password = var.db_password
}

# pgvector: the `vector` extension is created by the app's Alembic migration
# (`CREATE EXTENSION IF NOT EXISTS vector`). Cloud SQL for PostgreSQL 16 ships
# pgvector support, so no additional Terraform configuration is required here.
