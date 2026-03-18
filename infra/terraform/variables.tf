variable "project_id" {
  description = "Google Cloud project ID."
  type        = string
  default     = "gzguevara"
}

variable "region" {
  description = "Google Cloud region for Cloud Run and Artifact Registry."
  type        = string
  default     = "europe-west10"
}

variable "environment" {
  description = "Environment name used in resource naming."
  type        = string
  default     = "dev"
}

variable "frontend_service_name" {
  description = "Cloud Run service name for frontend."
  type        = string
  default     = "sql-agent-frontend"
}

variable "backend_service_name" {
  description = "Cloud Run service name for backend."
  type        = string
  default     = "sql-agent-backend"
}

variable "artifact_repository_id" {
  description = "Artifact Registry repository ID for app images."
  type        = string
  default     = "sql-agent-images"
}

variable "placeholder_frontend_image" {
  description = "Placeholder image for the frontend Cloud Run service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "placeholder_backend_image" {
  description = "Placeholder image for the backend Cloud Run service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "frontend_ingress" {
  description = "Ingress policy for frontend Cloud Run service."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "backend_ingress" {
  description = "Ingress policy for backend Cloud Run service."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "cloud_run_min_instance_count" {
  description = "Minimum number of Cloud Run instances."
  type        = number
  default     = 0
}

variable "cloud_run_max_instance_count" {
  description = "Maximum number of Cloud Run instances."
  type        = number
  default     = 1
}
