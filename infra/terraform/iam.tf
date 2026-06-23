resource "google_service_account" "run" {
  account_id   = "thesisos-run"
  display_name = "ThesisOS Cloud Run runtime service account"
}

locals {
  run_sa_roles = toset([
    "roles/aiplatform.user",
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
  ])
}

resource "google_project_iam_member" "run_sa" {
  for_each = local.run_sa_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.run.email}"
}
