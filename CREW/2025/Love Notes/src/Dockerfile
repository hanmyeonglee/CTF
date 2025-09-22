FROM node:22-slim
USER root

# Install MongoDB dependencies
RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . . 
RUN npm install
RUN chown -R node:node /app

USER node
EXPOSE 8000

# Start supervisord to manage MongoDB and the Node.js app
CMD ["npm", "start"]
