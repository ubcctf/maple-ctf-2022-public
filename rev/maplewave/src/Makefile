CFLAGS=-O2 -Wall $(shell pkg-config libpulse-simple --cflags)
LDFLAGS=-lm $(shell pkg-config libpulse-simple --libs)

maplewave: maplewave.o
	$(CC) $< -o $@ $(LDFLAGS)

.PHONY: clean

clean:
	rm -f maplewave *.o
