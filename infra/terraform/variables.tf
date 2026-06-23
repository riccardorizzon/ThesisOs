variable "project_id" {
  type        = string
  description = "GCP project ID that owns all ThesisOS resources."
}

variable "region" {
  type        = string
  description = "GCP region for all regional resources."
  default     = "europe-west1"
}

variable "db_tier" {
  type        = string
  description = "Cloud SQL machine tier. Smallest/cheapest tier by default."
  default     = "db-f1-micro"
}

# The real database password is managed in Secret Manager / a local tfvars file
# and is never committed. The empty default keeps `terraform validate` happy.
variable "db_password" {
  type        = string
  description = "Password for the Cloud SQL user; real value comes from Secret Manager / tfvars."
  sensitive   = true
  default     = ""
}
