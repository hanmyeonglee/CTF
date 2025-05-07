FROM --platform=linux/amd64 node:lts

WORKDIR /app
COPY .yarn .yarn
COPY package.json yarn.lock .yarnrc.yml ./
RUN yarn install
COPY . .
RUN yarn build
RUN yarn vite:build
CMD ["yarn", "start"]
