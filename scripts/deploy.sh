# 1) Build & push your images (examples in README)
export PROJECT_ID=your-project
export REGION=us
export REPO=ofc
# FE_IMAGE and BE_IMAGE should point at your pushed images
export FE_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/ofc-fe:latest"
export BE_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/ofc-be:latest"

# 2) Terraform
terraform init
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="region=us-central1" \
  -var="frontend_image=$FE_IMAGE" \
  -var="backend_image=$BE_IMAGE" \
  -var='fe_env={VITE_API_BASE="https://<backend-cloud-run-url>",VITE_WS_URL="wss://<backend-cloud-run-url>/ws"}'

