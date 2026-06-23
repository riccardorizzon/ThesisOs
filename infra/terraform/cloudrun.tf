resource "google_cloud_run_v2_service" "backend" {
  name     = "thesisos-backend"
  location = var.region

  template {
    service_account = google_service_account.run.email

    # Mount the Cloud SQL instance so the backend can reach Postgres over the
    # Cloud SQL Unix socket at /cloudsql/<connection_name>.
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.pg.connection_name]
      }
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/thesisos/backend:latest"

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      # DATABASE_URL is sourced from the `database-url` Secret Manager secret so
      # the connection string (incl. credentials) is never baked into the config.
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "VERTEX_LOCATION"
        value = var.region
      }
    }
  }

  depends_on = [
    google_project_service.services,
    google_secret_manager_secret.database_url,
    google_sql_database_instance.pg,
  ]
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

# Public (allUsers) invoker access is OPT-IN and OFF by default. These bindings
# are only created when var.allow_public_invoker is true, which is a deliberate
# choice; IAP or authenticated-invoker access is strongly preferred.
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  count    = var.allow_public_invoker ? 1 : 0
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  count    = var.allow_public_invoker ? 1 : 0
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
