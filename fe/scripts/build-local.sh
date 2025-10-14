#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PLAT=$(uname -m | grep -qi arm && echo linux/arm64 || echo linux/amd64)
docker buildx build --no-cache --platform "$PLAT" -t ofc-frontend:latest --load .
