FROM python:3

RUN apt-get update && apt-get -y install socat

WORKDIR /chal

RUN pip install --no-cache-dir pycryptodome

COPY . .

RUN adduser --system ctf
USER ctf:nogroup

CMD ["socat", "TCP-LISTEN:1337,fork,reuseaddr", "EXEC:'python ./server.py'"]
