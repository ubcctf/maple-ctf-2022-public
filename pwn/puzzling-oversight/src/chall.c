#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

int wincount;
unsigned short gamestate[8];
void (*menu[4])();


//intended solution: use out of bounds write in play() to write to menu's quit() fn pointer to change it to point to gamestate using offsets
//gamestate is in rwx .bss, which can run shellcode, so craft a clever <18 byte shellcode (including part of padding between wincount coz out of bounds is both ways) (or 14 byte very easily) using existing codes by playing the game and 0 to quit
//trigger shellcode with 4th option in menu, get shell

//potentially unintended solution: read libc addresses from plt and bruteforce system offset from there using libc database
//mitigation: statically link libc
//(honestly though that is a pretty valid solution so probably not gonna mitigate)

//potentially unwanted solution: read() calls to allow larger shellcode writes
//mitigation: seccomp but might give too much hint on what the expected shellcode might be



//assume min >= 0 && max < 1000000
int parseInput(int min, int max) {
    char buf[8];   //account for newline too

    if(!fgets(buf, 8, stdin)) {
        printf("Cannot read input, retrying...\n");
        return -1;
    }

    char* end;
    long val = strtol(buf, &end, 10);
    if(end == buf) {
        printf("Invalid number entered!\n");
        return -1;           
    }

    if(val < min || val > max) {
        printf("Invalid range entered!\n");
        return -1;
    }

    return val;
}


void play() {
    int* ref = (int*) gamestate;

    srand(time(0));

    int len = 4;
    while(len--) {
        ref[len] = rand();
    }

    while(1) {

        if(!ref[0] && !ref[1] && !ref[2] && !ref[3]) 
            break;
        
        printf("Board: ");
        int i = 8;
        while(i--)
            printf("%04x ", gamestate[i]);
        printf("\nYour move (0 to quit) > ");
        fflush(stdout);   //printf no newline without fflush will trip pwntools but thats more of a hassle than a challenge lol
        //edit: ended up adding setbuf anyways so technically redundant code here
        
        long index = parseInput(0, 8);
        if(index == -1) continue;
        if(index == 0) return;
        index = 8 - index;

        printf("Increment how much? > ");
        fflush(stdout);

        long count = parseInput(1, 0xFFFF);
        if(count == -1) continue;

        for(i = index-1; i <= index+1; i++) {
            gamestate[i] += (unsigned short) count;   //overflows should just be modulos
        }

    }

    printf("Congrats! You solved it!");

    wincount++;
}

void help() {
    printf("How to play this game:\n");
    printf("You are given 8 random hexadecimal numbers, which you can increment by any amount (it will wrap around if it's too big);\n");
    printf("However, the catch is doing so also affects the numbers directly next to it!\n");
    printf("Your goal is to flip all the numbers to 0s.\n");
    printf("That's it - simple, right?\n");
}

void stats() {
    //wincount red herring; ppl might be able to figure out its out of bounds overwrite using this too so its less guessy
    //edit: oops forgot padding exists in between lmao but hey crashing on going back into play should be obvious enough
    printf("You have won %d times in the current session. ", wincount);
    if(wincount < 10) {
        printf("Keep going!\n");
    } else if(wincount < 50) {
        printf("You are doing well!\n");
    } else if (wincount < 1337) {
        printf("You are truly a number flipping master!\n");
    } else {
        printf("Please take a break :')\n");
        exit(0);  //forced to take a break lmao
    }
}

void quit() {
    exit(0);
}


int main() {
    alarm(60);
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    //assigned here instead of initializer to let the variables be at the top without needing headers
    //which is realistically a scenario some programmers would take
    //but more importantly for the chall this will now be in .bss instead of .data which we need for the exploit to work
    //and also will result in messier decompilation for a better challenge
    menu[0] = play;
    menu[1] = help;
    menu[2] = stats;
    menu[3] = quit;

    printf("Welcome to the Number Flipper(TM) game v7.27!\n\n");
    
    while(1) {
        printf("Options:\n");
        printf("1 - play the game\n");
        printf("2 - display how to play this game\n");
        printf("3 - display game stats\n");
        printf("4 - quit\n\n");
        printf("> ");
        fflush(stdout);

        long val = parseInput(1, 4);
        if(val == -1) continue;

        printf("\n");

        menu[val-1]();

        printf("\n");
    }

    return 0;
}