#!/bin/bash
IMAGE="ghcr.io/${{ steps.prep.outputs.repo_lower }}:latest"
CONTAINER_NAME="catty-container"
echo "Pulling image: $IMAGE"
docker pull $IMAGE
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

docker run -d --name $CONTAINER_NAME -p 8181:8181 --restart unless-stopped -e DEPLOY_REF=${{ github.sha }} $IMAGE
docker image prune -f
