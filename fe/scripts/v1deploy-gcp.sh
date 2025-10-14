#!/usr/bin/env bash

set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:=us-central1}"
: "${REPO:=ofc}"
: "${SERVICE:=ofc-frontend}"

cd "$(dirname "${BASH_SOURCE[0]}")/.."

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"
gcloud config set project "${PROJECT_ID}" -q
gcloud run deploy "${SERVICE}" --image "${IMAGE}" --region "${REGION}" --platform managed --allow-unauthenticated --port 80 --set-env-vars SQLITE_PATH=/app/data/transactions.db,FRONTEND_ORIGIN=https://ofc-frontend-<hash>-uc.a.run.app
