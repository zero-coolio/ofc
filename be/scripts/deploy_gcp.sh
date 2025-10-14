
#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:=us-central1}"
: "${SERVICE:=ofc-backend}"
: "${REPO:=ofc}"
cd "$(dirname "${BASH_SOURCE[0]}")/.."
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"
gcloud config set project "${PROJECT_ID}" -q
gcloud run deploy "${SERVICE}" --image "${IMAGE}" --region "${REGION}" --platform managed --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --max-instances 5 --timeout 600 --set-env-vars "SQLITE_PATH=/app/data/transactions.db"
