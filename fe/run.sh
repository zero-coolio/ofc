
REGION="us-central1"
SERVICE="ofc-fe2"
IMAGE="us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-fe:latest"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
