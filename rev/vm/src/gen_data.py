import random
enc = b"\x6a\x5a\x30\x6e\x03\x71\x6e\x3f\x7e\x75\x79\x72\x24\x50\x57\x6e\x17\x3a\x11\x1b\x73\x2a\x26\x23\x4a\x57\x4e\x2c\x20\x0a\x28\x28\x6c\x21\x20\x47\x71\x0c\x22\x30\x1c\x70\x6d\x3b\x6c\x73\x57\x2a"
key = b'*~>,\xbcAg\xc0'
with open("data.txt", "w") as f:
    lines = []
    for i in range(256):
        lines.append(''.join('{:02x}\n'.format(random.randint(0,255))))
    for i in range(248,256,1):
        lines[i] = ''.join('{:02x}\n'.format(key[i-248]))
    for i in range(188,236,1):
        lines[i] = ''.join('{:02x}\n'.format(enc[i-188]))
    f.writelines(lines)
