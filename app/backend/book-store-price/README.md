Back End
----------
Back End
## How to run via Docker


### Command line
请切换到Backend目录下
```
docker build -t zengemily79/book-store-price:latest .
[//]: # (docker run -it --rm -p 5000:5000 zengemily79/book-store_price)
```
Push to docker-hub
```
docker push zengemily79/book-store-price:latest
```


```commandline
docker buildx build --platform linux/amd64,linux/arm64 -t book-store-price .
docker tag book-store-price 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store-price:latest
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store-price
docker push 961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store-price:latest
```

