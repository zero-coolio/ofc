#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
docker run -it --rm -p 5173:80 -e VITE_API_BASE="http://localhost:80" ofc-frontend:latest
