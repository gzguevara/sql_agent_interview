output "project_id" {
  description = "Active Google Cloud project ID."
  value       = var.project_id
}

output "region" {
  description = "Active Google Cloud region."
  value       = var.region
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository for app images."
  value       = google_artifact_registry_repository.app_images.id
}

output "frontend_cloud_run_url" {
  description = "Public URL for frontend Cloud Run service."
  value       = google_cloud_run_v2_service.frontend.uri
}

output "backend_cloud_run_url" {
  description = "Public URL for backend Cloud Run service."
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_runtime_service_account" {
  description = "Service account email used by frontend Cloud Run service."
  value       = google_service_account.frontend_runtime.email
}

output "backend_runtime_service_account" {
  description = "Service account email used by backend Cloud Run service."
  value       = google_service_account.backend_runtime.email
}

output "deployer_service_account" {
  description = "Service account email intended for deployment automation."
  value       = google_service_account.deployer.email
}

output "frontend_secret_ids" {
  description = "Secret Manager IDs created for frontend configuration."
  value       = sort(keys(google_secret_manager_secret.frontend))
}

output "backend_secret_ids" {
  description = "Secret Manager IDs created for backend configuration."
  value       = sort(keys(google_secret_manager_secret.backend))
}
