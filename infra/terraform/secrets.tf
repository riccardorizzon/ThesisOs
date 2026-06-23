resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

# Real DSN wired at apply time from tfvars + Cloud SQL connection name.
resource "google_secret_manager_secret_version" "database_url_placeholder" {
  secret = google_secret_manager_secret.database_url.id
  secret_data = "postgresql+psycopg://thesisos:${var.db_password}@/thesisos?host=/cloudsql/${google_sql_database_instance.pg.connection_name}"

  depends_on = [google_sql_database_instance.pg]
}

resource "google_secret_manager_secret" "vertex_config" {
  secret_id = "vertex-config"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}
