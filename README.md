# OFC v3 — Full-Stack Demo

- **Backend (FastAPI)**: Unrestricted CORS, /info, /health (build time), Services + Storage, SQLite in ./data
- **Frontend (React + Vite)**: Sidebar form, dashboard, output JSON, API Base field, build time banner
- **Dockerfiles**: Separate FE/BE with build-time args
- **Scripts**: Local dev & GCP Cloud Run build/deploy

## Quickstart
### Backend
```bash
cd be
./scripts/dev_local.sh
# http://localhost:8000/docs
```

### Frontend
```bash
cd fe
./scripts/dev_local.sh
# http://localhost:5173
```
