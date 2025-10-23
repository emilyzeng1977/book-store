# 使用 Alpine Linux 基础镜像
FROM alpine:latest

# 安装 OpenJDK 17
RUN apk add --no-cache openjdk17-jre

# 设置工作目录
WORKDIR /app

# 复制已构建好的 JAR 文件
COPY target/*.jar app.jar

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV JAVA_OPTS="-Xms256m -Xmx512m"

# 启动应用
ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -jar app.jar"]