FROM python:3.12-slim

WORKDIR /app

# 安装依赖
RUN pip install --no-cache-dir torch transformers flask

# 下载 ChatGLM2-6B 模型
# 注意：第一次运行会自动下载模型到 /root/.cache/huggingface
COPY start_chatglm.sh .

EXPOSE 8000
CMD ["bash", "start_chatglm.sh"]