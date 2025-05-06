FROM ubuntu@sha256:adbb90115a21969d2fe6fa7f9af4253e16d45f8d4c1e930182610c4731962658

RUN apt-get update -y
RUN apt-get install -y socat

COPY ./deploy/flag /flag
COPY ./deploy/chal /chal

RUN chmod 755 /chal
RUN chmod 440 /flag

EXPOSE 39020
CMD socat TCP-LISTEN:39020,reuseaddr,fork EXEC:/chal
