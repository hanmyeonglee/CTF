FROM maven:3.9.6-eclipse-temurin-22-jammy

RUN apt update && apt install gcc -y

WORKDIR /app
RUN useradd -m app

COPY ./deploy/ .

RUN SECRET_KEY=$(openssl rand -base64 32) && \
    sed -i "s|RANDOM_SECRET_KEY|$SECRET_KEY|g" /app/src/main/webapp/WEB-INF/web.xml

RUN mvn package
RUN chmod 777 /app/target/MemoService-0.0.1-SNAPSHOT/download
RUN chown app:app /app/target/tomcat/work/Tomcat/localhost/_


COPY flag.txt /flag.txt
COPY readflag.c /tmp/readflag.c

RUN chmod 440 /flag.txt
RUN gcc /tmp/readflag.c -o /readflag
RUN rm /tmp/readflag.c
RUN chmod 2555 /readflag

USER app

EXPOSE $PORT