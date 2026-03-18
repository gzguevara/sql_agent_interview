resource "google_service_account" "frontend_runtime" {
  account_id   = "sql-agent-frontend-sa"
  display_name = "SQL Agent Frontend Runtime SA"
}

resource "google_service_account" "backend_runtime" {
  account_id   = "sql-agent-backend-sa"
  display_name = "SQL Agent Backend Runtime SA"
}

resource "google_service_account" "deployer" {
  account_id   = "sql-agent-deployer-sa"
  display_name = "SQL Agent Deployer SA"
}
