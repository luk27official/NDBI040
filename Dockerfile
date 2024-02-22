FROM node:20-bullseye

# npm modules
WORKDIR /usr/app
COPY ./package.json ./
COPY ./package-lock.json ./
RUN npm i

# copy source code
COPY ./ ./

# start server
EXPOSE 3000
RUN chmod +x ./start.sh

CMD ["./start.sh"]