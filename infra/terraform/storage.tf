locals {
  bucket_purposes = toset([
    "documents",
    "exports",
    "temp",
    "logs",
  ])
}

resource "google_storage_bucket" "buckets" {
  for_each = local.bucket_purposes

  name     = "${var.project_id}-thesisos-${each.value}"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.services]
}
