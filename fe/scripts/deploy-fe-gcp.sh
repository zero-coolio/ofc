#!/usr/bin/env bash
set -euo pipefail

# --- required/optional vars ---
: "${PROJECT_ID:=nulleffect-qa}"
: "${REGION:=us-central1}"
: "${REPO:=ofc}"
: "${SERVICE:=ofc-frontend}"
: "${VITE_API_BASE:=http://localhost:8080}"

# --- preflight: tools ---
if ! command -v gcloud >/dev/null 2>&1; then
  echo "❌ gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ docker not found. Install Docker Desktop."
  exit 1
fi

cd "$(dirname "${BASH_SOURCE[0]}")/.."

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

# auth to Artifact Registry
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

# ensure buildx is ready
(docker buildx ls | grep -q '\*') || docker buildx create --use >/dev/null 2>&1 || true

# build & push multi-arch
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "${IMAGE}" \
  --build-arg VITE_API_BASE="${VITE_API_BASE}" \
  --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --push .

# deploy to Cloud Run
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --port 80

echo "✅ Deployed https://${SERVICE}-${PROJECT_ID}.a.run.app (actual URL may differ; check 'gcloud run services describe ${SERVICE} --region ${REGION} --format=value(status.url)')"

