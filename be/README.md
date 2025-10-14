# Backend (FastAPI) — OFC v3

- Unrestricted CORS (demo)
- `/info` returns static contact info
- `/health` returns build time
- Service + Repository layers
- SQLite at `./data/transactions.db`

## Local

```bash
cd be
./scripts/dev_local.sh
# http://localhost:8000/docs
```

## Build & Deploy (GCP Cloud Run)

```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1
cd be
./scripts/build_image_gcp.sh
./scripts/deploy_gcp.sh
```
