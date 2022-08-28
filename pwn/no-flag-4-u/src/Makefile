.PHONY: all

all: chal libno_flag_4_u.so

chal: chal.c
	gcc -fno-stack-protector -z execstack -no-pie -Wl,-z,norelro -o chal chal.c

libno_flag_4_u.so:
	cd no-flag-4-u/ && \
		/root/.cargo/bin/cargo build && \
		mv target/debug/libno_flag_4_u.so ../
