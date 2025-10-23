docker build -t bookstore-api:latest ./
docker run -p 8080:8080 -d --name bookstore-api bookstore-api:latest

#docker logs -f bookstore-api    # 查看日志
#docker stop bookstore-api       # 停止容器
#docker start bookstore-api      # 重启已停止的容器
#docker rm bookstore-api         # 删除容器