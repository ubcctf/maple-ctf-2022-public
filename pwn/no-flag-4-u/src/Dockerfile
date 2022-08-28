FROM ubuntu:20.04

RUN apt-get update && apt-get -y install xinetd

RUN useradd -M ctf

WORKDIR /ctf

COPY xinetd.conf ./
COPY banner_fail ./
COPY flag.txt ./
COPY challenge.sh ./
COPY run.sh ./
COPY chal ./
COPY libno_flag_4_u.so ./

CMD ["xinetd", "-d", "-dontfork", "-f", "xinetd.conf"]
