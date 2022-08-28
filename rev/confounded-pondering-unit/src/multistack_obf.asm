#include "isa.asm"

initstack 5
initstack 6
initstack 7

irmov 0xf1a9, r0                    ; r0 = &flag
mrmov 0(r0), r1                     ; r1 = flag
xor r14, r14                        ; r14 = 0 (win result)

irmov 0xb4a5_5f3e_60a4_1ca1, r2
mov r1, r8
xor r2, r8
irmov 0x450c_0f3e_60a4_1ca1, r3
sub r3, r8
irmov 0x1_0000_0000_0000, r2
div r2, r8
jne bad
call pass3, r6

pass3:
call pass2, r6
irmov 0x9f12_42ba_e034_7fc5, r8
mov r1, r2
xor r8, r2
irmov 0x0000_0000_ffff_0000, r3
and r3, r2
irmov 0x0000_0000_5af4_0000, r3
sub r3, r2
jne bad
irmov pass4, r11
push r11, r5
ret r7

bad:
halt

check2:
call check1, r7
irmov 0x1_0000_0000, r13
mov r0, r12
mul r13, r12
add r12, r14
ret r6

pass1:
call checks
ret r6

check1:
irmov 0x1_0000_0000_0000, r13
mov r0, r12
mul r13, r12
add r12, r14
ret

check4:
call check3, r7
add r0, r14
halt
#d "win!"

pass2:
call pass1, r6
irmov 0xf413_8fda_ef81_9a74, r2
mov r1, r8
xor r8, r2
irmov 0x0000_ffff_0000_0000, r3
and r3, r2 
irmov 0x0000_7ce7_0000_0000, r8
sub r2, r8
jne bad
irmov pass3, r11
push r11, r5
ret r7


check3:
call check2, r7
irmov 0x1_0000, r13
mov r0, r12
mul r13, r12
add r12, r14
ret r5

pass4:
irmov 0x462f_29fc_ab21_19ab, r8
mov r1, r2
xor r8, r2
irmov 0x0000_0000_0000_ffff, r3
and r3, r2
irmov 0x0000_0000_0000_5edc, r3
sub r3, r2
jne bad
ret r7

checks:
call check4, r7

#addr 0xf1a9
#d64 0x0000_0000_0000_0000
;#d64 0xf1a9_f33d_bac04_777