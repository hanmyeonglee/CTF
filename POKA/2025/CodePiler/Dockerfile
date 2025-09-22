FROM python:3.12-slim

RUN apt-get update && apt-get install -y gcc git iptables \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir flask requests markitdown python-dotenv

WORKDIR /app

RUN addgroup --system ctf && adduser --system --ingroup ctf --no-create-home --shell /bin/false ctf

COPY ./app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt

COPY readflag.c /readflag.c
RUN gcc /readflag.c -o /readflag && \
    chown root:root /readflag && \
    chmod 4755 /readflag && rm /readflag.c

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]