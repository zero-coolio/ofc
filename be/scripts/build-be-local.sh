#!/usr/bin/env bash
set -euo pipefail

# Always build from the backend root (where the Dockerfile lives)
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Detect platform automatically: Apple Silicon (arm64) or Intel (amd64)
PLAT=$(uname -m | grep -qi arm && echo linux/arm64 || echo linux/amd64)

# Build the image locally and load it into Docker
docker buildx build \
  --platform "$PLAT" \
  -t ofc-backend:latest \
  --load .


