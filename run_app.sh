#!/bin/bash
SHA=$1
IMAGE=$2
GITHUBTOKEN=$3
GITHUBACTOR=$4
CONTAINER_NAME="catty-container"

echo "Logging in GHCR"
echo "$GITHUBTOKEN" | docker login ghcr.io -u $GITHUBACTOR --password-stdin

echo "Pulling image: $IMAGE"
docker pull $IMAGE
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

docker run -d --name $CONTAINER_NAME -p 8181:8181 -e DEPLOY_REF=$SHA --restart unless-stopped $IMAGE
docker image prune -f
