#!/usr/bin/bash

sudo docker build -t maplectf-pwn-build - < build.dockerfile
sudo docker run --rm --mount type=bind,src="$(pwd)",dst=/mnt maplectf-pwn-build

cp \
    chal \
    libno_flag_4_u.so \
    run.sh \
    challenge.sh \
    xinetd.conf \
    banner_fail \
    Dockerfile \
    flag.txt \
    ../hosted/

cp \
    chal \
    libno_flag_4_u.so \
    run.sh \
    ../static/
