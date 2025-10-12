#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-web}"
SERVICE_NAME="${SERVICE_NAME:-ofc-fe}"
TAG="${TAG:-$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:${TAG}"
gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" >/dev/null 2>&1 ||   gcloud artifacts repositories create "$REPOSITORY" --location="$REGION" --repository-format=docker --description="Docker repo for OFC FE"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
docker build -t "$IMAGE_URI" .
docker push "$IMAGE_URI"
echo "$IMAGE_URI"
