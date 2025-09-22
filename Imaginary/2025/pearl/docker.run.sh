docker stop pearlc
docker container prune -f
docker build -t pearl .
docker run -p 3000:8080 --name pearlc pearl