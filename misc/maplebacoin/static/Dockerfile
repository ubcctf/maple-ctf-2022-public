FROM node:lts
RUN useradd service
COPY --chown=service ./src /home/service/
WORKDIR /home/service
RUN npm install -g patch-package
RUN npm install
RUN npx patch-package
EXPOSE 3000/tcp
CMD ["su", "-", "service", "-c", "./start.sh"]
