
//https://github.com/NicoHood/HID/blob/master/src/SingleReport/RawHID.h
#include "HID-Project.h"

//https://github.com/rweather/arduinolibs/tree/master/libraries/Crypto
#include <RNG.h>
#include <CTR.h>
#include <AES.h>

//need to set the following in RawHID.h
// #define RAWHID_USAGE_PAGE	0xFEED
// #define RAWHID_USAGE	   	0xFACE

uint8_t rawhid_buf[255];
uint16_t mapping[6] = {0x0100, 0x0200, 0x0001, 0x0002, 0xF0F0, 0x0F0F};    //opcode mapping
const char flag[] = "maple{h1d1n6_m4lw4r3_1n_f1rmw4r35}";
int printed = 0;

const char strs[] = "User32.dll\0CreateProcessA\0Kernel32.dll\0SendInput";

void setup() {
  RawHID.begin(rawhid_buf, sizeof(rawhid_buf));
  randomSeed(analogRead(0));
  RNG.begin(analogRead(0));   //buffer operations
}

void loop() {
  RNG.loop();   //RNG housekeeping

  int bytesAvailable = RawHID.available();
  
  //wait until available
  if(bytesAvailable >= 6) {

    //only continue if the header is correct
    if(RawHID.read() == 0x27 && RawHID.read() == 0x07) {
      
      //fetch secret
      uint8_t secret[4];

      for(int i = 0; i < 4; i++)
        secret[i] = RawHID.read();

      //generate payload 
      uint8_t send[64];    //no need to memset since random bytes are good noise anyway

      if(random(10)) {  //bigger chance to have normal input
        ((unsigned short*)send)[0] = 0xf00f;
        ((unsigned short*)send)[1] = mapping[random(6)];  //keycode

        RNG.rand(&send[8], 56);    //fill rest with random bytes
      } else {   //generate backdoor that prints flag char by char into file
        ((unsigned short*)send)[0] = 0x0ff0;

        if(strlen(flag) == printed) exit(0);  //we are done printing the flag, time to halt (reset to resend)

        char cmd[32] = "cmd.exe /c echo|set/p=\"A\">>conf";   //A is placeholder
        cmd[23] = flag[printed++];
        //memcpy(&send[36], cmd, strlen(cmd) + 1);

        RNG.rand(&send[4], 28);    //generate key

        //encrypt - reuse opcode for key to fit everything nicely and aes is not vulnerable to partial key exposure
        CTR<AES256> aes;
        aes.setKey(send, 32);
        aes.setIV(&strs[32], 16);
        aes.setCounterSize(16);
        aes.encrypt(&send[32], cmd, 32);
      }

      //xor payload with secret
      int i = 64;
      while(i--) {
          send[i] = send[i] ^ secret[i % 4];
      }

      RawHID.write(send, sizeof(send));
    }

    //consume and discard the rest of the bytes sent for the next round
    while((bytesAvailable--) - 6)
      RawHID.read();

    //emulate next input delay
    delay(random(500));
  }
}

