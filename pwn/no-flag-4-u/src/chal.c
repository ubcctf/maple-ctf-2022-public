#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

long get_input() {
    char input[0x100];

    gets(input);

    return atol(input);
}

void create_page(void** pages) {
    printf("index: ");
    long index = get_input();

    printf("size: ");
    long size = get_input();

    pages[index] = malloc(size);

    printf("content: ");
    gets(pages[index]);
}

void win() {
    execl("/bin/cat", "/bin/cat", "flag.txt", NULL);
}

void edit_page(void** pages) {
    printf("index: ");
    long index = get_input();

    printf("content: ");
    gets(pages[index]);
}

void print_page(void** pages) {
    printf("index: ");
    long index = get_input();

    printf(pages[index]);
    printf("\n");
}

void delete_page(void** pages) {
    printf("index: ");
    long index = get_input();

    free(pages[index]);
}

int main() {
    alarm(60);
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    void* pages[0x10];
    long input;

    while (1) {
        puts("1 : Create page");
        puts("2 : Edit page");
        puts("3 : Print page");
        puts("4 : Delete page");
        puts("5 : Exit");
        input = get_input();
        switch (input) {
            case 1:
                create_page(pages);
                break;
            case 2:
                edit_page(pages);
                break;
            case 3:
                print_page(pages);
                break;
            case 4:
                delete_page(pages);
                break;
            case 5:
                return 0;
        }
    }
}
