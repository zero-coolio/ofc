#!/usr/bin/env bash
set -euo pipefail
npm ci || npm install
npm run build
