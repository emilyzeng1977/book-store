# 使用官方 Python 3.12 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 更新包管理器并安装 curl
RUN apt-get update && apt-get install -y curl iputils-ping && apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制当前目录所有文件到容器中的工作目录，包括 newrelic.ini
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量指向配置文件
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

# 暴露端口
EXPOSE 5000

# 设置容器启动命令，使用 newrelic-admin 启动
CMD ["newrelic-admin", "run-program", "python", "main.py"]
