# Terraform Infrastructure (Google Cloud)

This folder provisions only infrastructure for the SQL agent project:

- Artifact Registry repository for frontend/backend images
- Secret Manager secret placeholders (no values)
- Service accounts and IAM bindings
- Public frontend and backend Cloud Run services using placeholder images

## Inputs preconfigured from planning

- Project: `gzguevara`
- Region: `europe-west10` (Berlin)
- Terraform state: local
- Cloud Run exposure: public frontend and public backend

## Prerequisites

1. Install Terraform `>= 1.6`.
2. Authenticate with Google Cloud:
   - `gcloud auth application-default login`
   - `gcloud config set project gzguevara`
3. Enable required APIs manually (as requested):
   - Cloud Run Admin API
   - Artifact Registry API
   - Secret Manager API
   - IAM API
   - Cloud Resource Manager API

## Usage

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Notes

- Secret Manager entries are created as placeholders only. Add secret values later via:
  - Google Cloud Console, or
  - `gcloud secrets versions add ...`
- Cloud Run services use public placeholder images by default:
  - `us-docker.pkg.dev/cloudrun/container/hello`
- Once real application images exist, update:
  - `placeholder_frontend_image`
  - `placeholder_backend_image`
