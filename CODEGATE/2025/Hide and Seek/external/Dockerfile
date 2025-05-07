FROM node:20-alpine

COPY ./ /app
WORKDIR /app
RUN npm i

EXPOSE 3000

RUN npm run build

CMD ["npm", "run", "start"]
