from pwn import * 
from math import sin, cos, tan, pi
from Crypto.Util.number import *
import sys

r = remote(sys.argv[1], int(sys.argv[2]))

def get_enc(angle):
    r.sendline(b'3')
    r.sendline(str(cos(angle)))
    r.sendline(str(sin(angle)))
    r.sendline(str(-sin(angle)))
    r.recvuntil(b'base.q2.y:')
    r.sendline(str(cos(angle)))
    resp = r.recvuntil(b'\n\n').strip()
    return resp


SMP = 333
LEN = 352
cnt = [0 for _ in range(LEN)]

for _ in range(SMP):
    print("at iteration ", _, end='\r')
    for i, b in enumerate(get_enc(-pi/4)):
        if b == ord('1'):
            cnt[i] += 1
print()
dec = "".join('1' if x > SMP//2 else '0' for x in cnt)
ans = long_to_bytes(int(dec,2))
print("the convincingness of this solution is: ", min([abs(x-SMP//2) for x in cnt]))
print(ans)
