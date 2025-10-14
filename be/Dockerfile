
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /app/data
ENV SQLITE_PATH=/app/data/transactions.db
ARG BUILD_TIME
ENV BUILD_TIME=$BUILD_TIME
EXPOSE 8080
CMD ["bash","-lc","exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
