#!/bin/bash

REGION="ap-southeast-2"
ACCOUNT_ID="961341537777"
REPO="book-store"
TAG="latest"

# 登录
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# 打标签
docker tag zengemily79/book-store:$TAG $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$TAG

# 推送
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:$TAG
