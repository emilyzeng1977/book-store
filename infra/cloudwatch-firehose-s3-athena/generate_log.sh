#!/bin/bash

GROUP_NAME="/ecs/book_store"
STREAM_NAME="my-test-stream"
MESSAGE="Hello from CLI"
TIMESTAMP=$(gdate +%s%3N)

# Create log stream if not exist
aws logs describe-log-streams --log-group-name "$GROUP_NAME" --log-stream-name-prefix "$STREAM_NAME" | grep "$STREAM_NAME" >/dev/null || \
  aws logs create-log-stream --log-group-name "$GROUP_NAME" --log-stream-name "$STREAM_NAME"

# 获取 sequence token（首次写入时为 None）
SEQUENCE_TOKEN=$(aws logs describe-log-streams \
  --log-group-name "$GROUP_NAME" \
  --log-stream-name-prefix "$STREAM_NAME" \
  --query "logStreams[0].uploadSequenceToken" \
  --output text)

# 发送日志
if [ "$SEQUENCE_TOKEN" == "None" ] || [ -z "$SEQUENCE_TOKEN" ]; then
  aws logs put-log-events \
    --log-group-name "$GROUP_NAME" \
    --log-stream-name "$STREAM_NAME" \
    --log-events timestamp=$TIMESTAMP,message="$MESSAGE"
else
  aws logs put-log-events \
    --log-group-name "$GROUP_NAME" \
    --log-stream-name "$STREAM_NAME" \
    --log-events timestamp=$TIMESTAMP,message="$MESSAGE" \
    --sequence-token "$SEQUENCE_TOKEN"
fi