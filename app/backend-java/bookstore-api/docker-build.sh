docker build -t zengemily79/bookstore-api:latest ./
docker run -d -p 8080:8080 --name bookstore-api zengemily79/bookstore-api:latest
# docker pull zengemily79/bookstore-api:latest
# docker logs -f bookstore-api    # 查看日志
# docker stop bookstore-api       # 停止容器
# docker start bookstore-api      # 重启已停止的容器
# docker rm bookstore-api         # 删除容器
# docker rmi zengemily79/bookstore-api:latest  # 删除镜像

aws ecr get-login-password --region ap-east-1 | docker login --username AWS --password-stdin 377977679134.dkr.ecr.ap-east-1.amazonaws.com
docker tag zengemily79/bookstore-api:latest 377977679134.dkr.ecr.ap-east-1.amazonaws.com/bookstore-api:latest
docker push 377977679134.dkr.ecr.ap-east-1.amazonaws.com/bookstore-api:latest
