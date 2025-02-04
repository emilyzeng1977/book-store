# 使用官方 Python 3.12 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 更新包管理器并安装 curl
RUN apt-get update && apt-get install -y curl iputils-ping && apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 到容器
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录所有文件到容器中的工作目录
COPY . .

# 暴露端口 5000
EXPOSE 5000

# 设置容器启动时执行的命令
CMD ["python", "main.py"]