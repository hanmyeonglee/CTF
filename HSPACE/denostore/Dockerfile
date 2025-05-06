FROM denoland/deno:alpine-1.46.3

WORKDIR /app

COPY . .

CMD ["deno", "run", "--allow-read", "--deny-read=/proc/self/environ,.env", "--allow-write=./db", "--unstable-kv", "--allow-net", "--allow-env=SECRET_KEY", "--deny-env=FLAG", "main.js"]
