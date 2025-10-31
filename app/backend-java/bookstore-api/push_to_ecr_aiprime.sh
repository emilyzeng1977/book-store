#!/bin/bash

REGION="ap-east-1"
ACCOUNT_ID="377977679134"
REPO="tom-demo-ecr-dev"
TAG="1.0.1"

IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO}:${TAG}"

docker pull zengemily79/bookstore-api:latest
# 1. 给本地镜像打 ECR 标签
docker tag zengemily79/bookstore-api:latest "${IMAGE_URI}"

# 2. 登录 AWS ECR
aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# 3. 推送镜像到 ECR
docker push "${IMAGE_URI}"