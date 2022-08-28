FROM node:lts
RUN useradd service
COPY --chown=service ./src /home/service/
WORKDIR /home/service
RUN npm install
USER service
EXPOSE 3000/tcp
CMD ["npm", "run", "start"]
