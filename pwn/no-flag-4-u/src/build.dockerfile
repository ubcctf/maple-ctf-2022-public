FROM ubuntu:20.04

RUN apt-get update && apt-get -y install build-essential curl

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- --default-toolchain nightly --profile minimal -y

WORKDIR /mnt

CMD make
