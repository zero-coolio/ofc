#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-web}"
SERVICE_NAME="${SERVICE_NAME:-ofc-fe}"
TAG="${1:-latest}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:${TAG}"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com --project "$PROJECT_ID"
gcloud run deploy "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --image "$IMAGE_URI" --allow-unauthenticated --port 8080 --memory 512Mi --max-instances 3 --platform managed
