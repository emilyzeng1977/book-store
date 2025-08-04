# 使用官方 Python 3.12 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录所有文件到容器中的工作目录
COPY . .

# 设置环境变量指向配置文件
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

# 暴露端口 5000
EXPOSE 5000

# 设置容器启动命令，使用 newrelic-admin 启动
CMD ["newrelic-admin", "run-program", "python", "main.py"]