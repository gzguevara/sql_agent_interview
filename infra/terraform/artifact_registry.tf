resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = var.artifact_repository_id
  format        = "DOCKER"
  description   = "Docker images for sql-agent frontend and backend."
}
