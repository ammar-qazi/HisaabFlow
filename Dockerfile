# syntax=docker/dockerfile:1

# 1. Build the React frontend
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# 2. Python app serving the API and the built frontend on one port
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HISAABFLOW_CONFIG_DIR=/data/configs \
    HISAABFLOW_FRONTEND_DIR=/app/frontend/build
WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
# Shipped configs; the entrypoint copies any the user doesn't have yet into /data
COPY configs/ configs-default/
COPY --from=frontend /app/frontend/build frontend/build
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

EXPOSE 8000
VOLUME ["/data"]
ENTRYPOINT ["entrypoint.sh"]
# Requests are logged by backend/api/middleware.py, so uvicorn's access log is off
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
