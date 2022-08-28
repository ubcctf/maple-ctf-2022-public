#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void vuln() {
    char buf[0x100];

    puts("What's your name?");
    read(0, buf, 0x1337);
    printf("Hello %s!\n", buf);

    puts("How old are you?");
    read(0, buf, 0x1337);
    printf("Wow, I'm %s too!\n", buf);
}

int main() {
    alarm(60);
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    vuln();

    return 0;
}
