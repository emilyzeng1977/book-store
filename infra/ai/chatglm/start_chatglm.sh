#!/bin/bash
# 启动 ChatGLM 本地 API
python -m transformers_cli serve --model_name THUDM/chatglm2-6b --host 0.0.0.0 --port 8000