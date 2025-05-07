FROM node:20-bullseye-slim

RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libx11-xcb1 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/

WORKDIR /app

RUN npm install

EXPOSE 3000

CMD ["node", "index.js"]
