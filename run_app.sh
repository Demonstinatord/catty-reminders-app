#!/bin/bash
SHA=$1
IMAGE=$2
CONTAINER_NAME="catty-container"
echo "Pulling image: $IMAGE"
docker pull $IMAGE
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

docker run -d --name $CONTAINER_NAME -p 8181:8181 --restart unless-stopped $IMAGE
docker image prune -f
