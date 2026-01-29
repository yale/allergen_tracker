#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/.env.deploy" ]; then
  source "$SCRIPT_DIR/.env.deploy"
else
  echo "Error: .env.deploy not found. Copy .env.deploy.example to .env.deploy and fill in your values."
  exit 1
fi

echo "Deploying to ${DEPLOY_HOST}..."

ssh -t "${DEPLOY_USER}@${DEPLOY_HOST}" -p ${DEPLOY_PORT} "source ~/.zprofile && cd ${PROJECT_PATH} && \
  git pull && \
  docker-compose down && \
  docker-compose up -d --build && \
  docker image prune -f"

echo "Deployment complete!"
