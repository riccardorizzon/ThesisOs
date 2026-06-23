resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

# Placeholder version so `secret_key_ref database-url:latest` resolves at apply
# time (the Cloud Run revision needs an existing version to roll out). The runbook
# adds the REAL DSN as a new version, which then becomes `latest`.
resource "google_secret_manager_secret_version" "database_url_placeholder" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "postgresql+psycopg://REPLACE_VIA_RUNBOOK@/thesisos"
}

resource "google_secret_manager_secret" "vertex_config" {
  secret_id = "vertex-config"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}
