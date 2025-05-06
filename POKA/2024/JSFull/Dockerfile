FROM node:current-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV FLAG=pokactf2024{test}

RUN apt update \
 && apt install -y wget gnupg \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
 && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
 && apt update && apt install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

COPY app /app
WORKDIR /app
RUN npm install

EXPOSE 30000

CMD ["node", "index.js"]