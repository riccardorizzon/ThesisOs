locals {
  gcp_services = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
  ])
}

resource "google_project_service" "services" {
  for_each = local.gcp_services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
