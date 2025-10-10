
REGION="us-central1"
SERVICE="ofc-backend"
IMAGE="us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-be:latest"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
