Back End
----------
Back End
## How to run via Docker


### Command line
请切换到Backend目录下
```
docker build -t zengemily79/book_store:latest .
docker build -t zengemily79/book_store_no_db:latest -f Dockerfile_no_db .
[//]: # (docker run -it --rm -p 5000:5000 zengemily79/book_store)
```
Push to docker-hub
```
docker push zengemily79/book_store_no_db:latest
```

