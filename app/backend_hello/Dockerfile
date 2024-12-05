# 使用官方 Python 3.12 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目的依赖文件和源代码
COPY requirements.txt ./
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 默认的运行端口
EXPOSE 5000

# 指定容器启动时运行的命令
CMD ["python", "main.py"]
