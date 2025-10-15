#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:=nulleffect-qa}"
: "${REGION:=us-central1}"
: "${REPO:=ofc}"
: "${SERVICE:=ofc-frontend}"
: "${VITE_API_BASE:=http://localhost:8080}"
cd "$(dirname "${BASH_SOURCE[0]}")/.."
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
(docker buildx ls | grep -q '\*') || docker buildx create --use >/dev/null 2>&1 || true
docker buildx build --platform linux/amd64,linux/arm64 -t "${IMAGE}" --build-arg VITE_API_BASE="${VITE_API_BASE}" --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" --push .
