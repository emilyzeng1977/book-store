# 使用 Alpine Linux 基础镜像
FROM alpine:latest

# 安装 OpenJDK 17
RUN apk add --no-cache openjdk17-jre

# 设置工作目录
WORKDIR /app

# 安装 curl 以下载 Datadog Java Agent
RUN apk add --no-cache curl

# 下载 Datadog Java Agent
RUN curl -L -o dd-java-agent.jar https://dtdg.co/latest-java-tracer

# 复制已构建好的 JAR 文件
COPY target/*.jar app.jar

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV JAVA_OPTS="-Xms256m -Xmx512m"

# 启动命令：启用 Datadog Java Agent，但不在 Dockerfile 内设置任何 DD_* 环境变量
ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -javaagent:/app/dd-java-agent.jar -jar /app/app.jar"]