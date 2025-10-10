docker buildx create --use || true

docker buildx build \
  --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-fe:latest \
  --push .

