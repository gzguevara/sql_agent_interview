locals {
  name_prefix = "sql-agent-${var.environment}"

  frontend_secret_ids = toset([
    "frontend-backend-base-url",
    "frontend-auth-redirect-uri",
    "frontend-auth-cookie-secret",
    "frontend-auth-client-id",
    "frontend-auth-client-secret",
    "frontend-auth-server-metadata-url",
    "frontend-auth-expose-tokens",
  ])

  backend_secret_ids = toset([
    "backend-google-api-key",
    "backend-google-oauth-client-id",
    "backend-allowed-emails",
    "backend-model-name",
    "backend-database-url",
    "backend-app-name",
    "backend-log-level",
  ])

  frontend_secret_members = {
    for secret_id in local.frontend_secret_ids :
    secret_id => "serviceAccount:${google_service_account.frontend_runtime.email}"
  }

  backend_secret_members = {
    for secret_id in local.backend_secret_ids :
    secret_id => "serviceAccount:${google_service_account.backend_runtime.email}"
  }
}
