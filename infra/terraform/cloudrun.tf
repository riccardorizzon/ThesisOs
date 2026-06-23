resource "google_cloud_run_v2_service" "backend" {
  name     = "thesisos-backend"
  location = var.region

  template {
    service_account = google_service_account.run.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/thesisos/backend:latest"

      # Placeholder value to keep the config minimal but valid. In a real deploy
      # DATABASE_URL is wired to the `database-url` Secret Manager secret.
      env {
        name  = "DATABASE_URL"
        value = "postgresql://thesisos@/thesisos"
      }
    }
  }

  depends_on = [google_project_service.services]
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = "thesisos-frontend"
  location = var.region

  template {
    service_account = google_service_account.run.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/thesisos/frontend:latest"
    }
  }

  depends_on = [google_project_service.services]
}

# Single-user app: both services are open to the public (allUsers) for now.
# This can be locked down later (e.g. IAP or authenticated invoker only).
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
