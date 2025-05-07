FROM node:22

RUN apt update && apt install gcc
WORKDIR /app
COPY ./app/package.json /app/package.json
RUN npm install 

COPY flag.txt /flag.txt
COPY readflag.c /tmp/readflag.c

RUN chmod 440 /flag.txt
RUN gcc /tmp/readflag.c -o /readflag
RUN rm /tmp/readflag.c
RUN chmod 2555 /readflag
COPY ./app /app
RUN mkdir /app/uploads/
RUN chmod 777 /app/uploads/

RUN useradd -m app
USER app
ENV NODE_ENV=production
CMD ["node","app.js"]