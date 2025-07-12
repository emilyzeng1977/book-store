#!/bin/bash

REGION="ap-southeast-2"
ACCOUNT_ID="961341537777"
REPO="book-store-price"
TAG="latest"

docker buildx build --platform linux/amd64,linux/arm64 -t ${REPO} .
# 打标签
docker tag ${REPO} ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO}:${TAG}
# 登录
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
# 推送
docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/${REPO}:$TAG