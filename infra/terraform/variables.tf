variable "project_id" {
  type        = string
  description = "GCP project ID that owns all ThesisOS resources."
}

variable "region" {
  type        = string
  description = "GCP region for all regional resources."
  default     = "europe-west1"
}

variable "vertex_location" {
  type        = string
  description = "Vertex AI location used by Gemini models."
  default     = "global"
}

variable "gemini_model" {
  type        = string
  description = "Gemini response model used for conversation and writing."
  default     = "gemini-3.6-flash"
}

variable "gemini_orchestration_model" {
  type        = string
  description = "Gemini model used for supervisor, planner, and router decisions."
  default     = "gemini-3.5-flash-lite"
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

# Public (allUsers) invoker access is OPT-IN and OFF by default. Enabling it is a
# deliberate choice; IAP or authenticated-invoker access is strongly preferred.
variable "allow_public_invoker" {
  type        = bool
  description = "When true, grant roles/run.invoker to allUsers (public access). Off by default."
  default     = false
}
