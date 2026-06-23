resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret" "vertex_config" {
  secret_id = "vertex-config"

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}
