.PHONY: all

all: chal

chal: chal.c
	gcc -fno-stack-protector -Wl,-z,relro,-z,now -o chal chal.c
