FROM python:alpine

RUN apk update && apk add socat

WORKDIR /app

COPY chal.py .
RUN addgroup -S ctf && adduser -S ctf -G ctf

USER ctf
CMD ["socat", "TCP-LISTEN:3333,fork,reuseaddr", "EXEC:'python ./chal.py'"]
