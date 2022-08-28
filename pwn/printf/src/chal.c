#include <stdio.h>
#include <unistd.h>

char s[0x100];

void go() {
    fgets(s, sizeof(s), stdin);
    printf(s);
}

void set() {
    go();
}

void ready() {
    set();
}

int main() {
    alarm(60);
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    ready();
    return 0;
}
