import random
import binascii
flag = b"maple{the_4lag_shOUld_Not_be_put_1N_initial_RAM}"

s = [0] * 128
key = random.randbytes(8)
print(b"Key ", key)
for i in range(0,128):
    s[i] = i
j = 0
for i in range(0,128):
    j = (j + s[i] + key[i % 8]) % 128
    tmp = s[i]
    s[i] = s[j]
    s[j] = tmp
j = 0
i = 0
enc = b''
while True:
    i = (i + 1) % 128
    j = (j + s[i]) % 128
    tmp = s[i]
    s[i] = s[j]
    s[j] = tmp
    k = s[(s[i]+s[j])%128]
    enc += bytes([k^flag[i-1]])
    print(k)
    if i == 48:
        break
print(''.join('{:02x} '.format(x) for x in enc))