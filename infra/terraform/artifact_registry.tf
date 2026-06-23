resource "google_artifact_registry_repository" "thesisos" {
  location      = var.region
  repository_id = "thesisos"
  format        = "DOCKER"
  description   = "Container images for ThesisOS backend and frontend."

  depends_on = [google_project_service.services]
}
