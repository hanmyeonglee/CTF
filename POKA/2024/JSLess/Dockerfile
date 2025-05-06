FROM php:apache

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV FLAG=pokactf2024{test}

RUN apt update \
 && apt install -y curl wget gnupg \
 && curl -sL https://deb.nodesource.com/setup_22.x | bash - \
 && apt-get install nodejs --yes \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
 && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
 && apt update && apt install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

COPY html /var/www/html

COPY app /app
WORKDIR /app
RUN npm install

EXPOSE 80 8080

CMD ["sh", "-c", "service apache2 start && node index.js"]