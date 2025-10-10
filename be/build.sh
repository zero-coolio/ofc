
PROJECT_ID="nulleffect-qa"
REGION="us-central1"
IMAGE="us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-be:latest"

# Auth Docker to Artifact Registry in this region
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build & push (from your ./be folder containing the Dockerfile)
cd be
docker build -t "$IMAGE" .
docker push "$IMAGE"
