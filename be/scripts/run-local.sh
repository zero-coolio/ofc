docker run -it --rm \
  -p 8080:8080 \
  -e PORT=8080 \
  -v "$(pwd)/data:/app/data" \
  ofc-backend:latest

