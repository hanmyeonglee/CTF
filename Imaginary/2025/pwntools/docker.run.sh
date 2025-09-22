docker stop pwnc
docker container prune -f
docker build -t pwn .
docker run -p 3000:8080 --name pwnc pwn