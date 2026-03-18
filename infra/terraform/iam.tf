resource "google_secret_manager_secret_iam_member" "frontend_secret_access" {
  for_each = local.frontend_secret_members

  secret_id = google_secret_manager_secret.frontend[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "google_secret_manager_secret_iam_member" "backend_secret_access" {
  for_each = local.backend_secret_members

  secret_id = google_secret_manager_secret.backend[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "google_project_iam_member" "deployer_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_project_iam_member" "deployer_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_project_iam_member" "deployer_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.deployer.email}"
}
