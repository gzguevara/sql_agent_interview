resource "google_secret_manager_secret" "frontend" {
  for_each = local.frontend_secret_ids

  secret_id = each.value

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "backend" {
  for_each = local.backend_secret_ids

  secret_id = each.value

  replication {
    auto {}
  }
}
