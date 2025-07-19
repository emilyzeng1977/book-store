Back End
----------
Back End
## How to run via Docker


### Command line
请切换到Backend目录下
```
docker build -t zengemily79/book-store:latest .
[//]: # (docker run -it --rm -p 5000:5000 zengemily79/book-store)
```
运行docker-compose
```
docker-compose up
docker-compose up -d // 希望在后台运行服务
docker-compose down
docker-compose stop // 只想停止服务而不删除容器
docker-compose restart
lsof -i :<端口号>
```

Push to docker-hub
```
docker push zengemily79/book-store:latest
```

```commandline
docker buildx build --platform linux/amd64,linux/arm64 -t zengemily79/book-store:latest --push .
docker buildx build --platform linux/amd64,linux/arm64 -t zengemily79/book-store:1.0.0-SNAPSHOT --push .
```
```commandline
docker buildx build --platform linux/amd64,linux/arm64 -t book-store .
docker tag book-store 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store:latest
// aws ecr create-repository --repository-name book-store --region ap-southeast-2
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store
docker push 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store:latest

```
repositoryArn: arn:aws:ecr:ap-southeast-2:961341537777:repository/book-store
repositoryUri: 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store

