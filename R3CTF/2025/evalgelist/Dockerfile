FROM php:7.3-fpm-alpine

LABEL auther_template="CTF-Archives"

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories  &&\
    apk add --update --no-cache nginx bash

COPY ./service/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY ./config/nginx.conf /etc/nginx/nginx.conf

COPY src /var/www/html

RUN chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

EXPOSE 80

VOLUME ["/var/log/nginx"]

ENTRYPOINT [ "/docker-entrypoint.sh" ]