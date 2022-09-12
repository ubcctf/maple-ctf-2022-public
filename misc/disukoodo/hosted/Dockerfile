FROM ubuntu:20.04

RUN apt-get update && apt-get -y install python3 python3-pip

RUN python3 -m pip install discord.py==1.7.3

RUN useradd -M ctf

WORKDIR /ctf

COPY bot.py ./

CMD ["python3", "bot.py"]