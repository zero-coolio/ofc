
#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:=nulleffect-qa}"
: "${REGION:=us-central1}"
: "${REPO:=ofc}"
: "${SERVICE:=ofc-backend}"
cd "$(dirname "${BASH_SOURCE[0]}")/.."
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"
gcloud artifacts repositories create "${REPO}" --repository-format=docker --location="${REGION}" --description="OFC images" || true
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
docker buildx create --use >/dev/null 2>&1 || true
docker buildx build --platform linux/amd64 --build-arg BUILD_TIME="$(date -u +"%Y-%m-%dT%H:%M:%SZ")" -t "${IMAGE}" --push .
echo "${IMAGE}" > scripts/.last_image
echo "Built and pushed ${IMAGE}"
