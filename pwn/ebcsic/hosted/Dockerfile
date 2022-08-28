FROM ubuntu:22.04

RUN apt-get update && apt-get install -y xinetd python3
RUN adduser --no-create-home --disabled-password --gecos "" ctf

COPY chal.py /app/chal.py
COPY flag /flag
COPY xinetd.conf /etc/xinetd.d/chal

EXPOSE 1337
CMD ["/usr/sbin/xinetd", "-d", "-dontfork"]
