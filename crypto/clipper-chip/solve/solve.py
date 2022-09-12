#!/usr/bin/env python3

from rich.progress import track
from z3 import Solver, BitVec, BitVecVal, Extract, If, LShR

REG0_SIZE = 17
REG1_SIZE = 19
REG2_SIZE = 31

REG0_TAPS = 0x100AB
REG1_TAPS = 0x40112
REG2_TAPS = 0x40000576


def reverse_bits(n, x):
    return int("".join(reversed(f"{x:b}".zfill(n))), 2)


def extract(hi, lo, x):
    return int("".join(reversed(f"{x:067b}"))[lo:hi], 2)


class LFSR:
    def __init__(self, size: int, taps: int, seed: int):
        self.size = size
        self.reg = seed
        self.taps = taps

    def step(self):
        lsb = self.reg & 1
        self.reg >>= 1
        if lsb:
            self.reg ^= self.taps
        return lsb


# We really need only a few pieces of information from the silicon: the sizes of
# the LFSRs, the taps, and the combining function: a&b | a&c | b&c.  For the
# purposes of checking our work, we reimplement the cipher in Python.
class Cipher:
    def __init__(self, key):
        self.reg0 = LFSR(REG0_SIZE, REG0_TAPS, extract(17, 0, key))
        self.reg1 = LFSR(REG1_SIZE, REG1_TAPS, extract(36, 17, key))
        self.reg2 = LFSR(REG2_SIZE, REG2_TAPS, extract(67, 36, key))

    def step(self):
        a = self.reg0.step()
        b = self.reg1.step()
        c = self.reg2.step()
        return a & b | a & c | b & c

    def encrypt(self, pt):
        out = bytearray()
        for b in pt:
            for i in range(7, -1, -1):
                k = self.step()
                b ^= k << i
            out.append(b)
        return bytes(out)


# We know the (extended) flag format, and this becomes our known plaintext.
ciphertext = bytes.fromhex(
    "18a6897ee801b2501a785d6a5909684a55aa2bc270b86904bb82037816a587c91a63b9e1d5dfc8eef1dda67b39008d1ee8e8dc0e1b9095"
)
plaintext = b"flag: maple{"

# Extract the keystream from the known plaintext and ciphertext.
known = len(plaintext)
keystream = int.from_bytes(bytes(x ^ y for x, y in zip(ciphertext, plaintext)), "big")

# We execute a correlation attack: the two smaller registers are *very* small
# (17 and 19 bits, respectively).  Examine the combining function:
#
#   +-------+---+
#   | a b c | f |
#   +-------+---+
#   | 0 0 0 | 0 |
#   | 0 0 1 | 0 |
#   | 0 1 0 | 0 |
#   | 0 1 1 | 1 |
#   | 1 0 0 | 0 |
#   | 1 0 1 | 1 |
#   | 1 1 0 | 1 |
#   | 1 1 1 | 1 |
#   +-------+---+
#
# If we set a to 1, 50% of the time, the output f will also be 1.  The same goes
# for 0, as well as a, b, and c.
#
# To mount the attack, we guess the contents of a register, picking the bits
# that cause the output to correlate with the known portion of the keystream.
def solve_reg(size, polynomial):
    result = []
    for i in track(range(1, 1 << size), f"solving {size}"):
        reg = LFSR(size, polynomial, i)
        s = 0
        for j in range(8 * known - 1, -1, -1):
            s += (keystream >> j) & 1 == reg.step()
        result.append((i, s))

    return max(result, key=lambda r: r[1])[0]


# Solve for the lowest bits of the key.
key0 = solve_reg(REG0_SIZE, REG0_TAPS)
key1 = solve_reg(REG1_SIZE, REG1_TAPS)

# Now that we have the contents of the two smaller registers, we can reconstruct
# the contents of the largest:
#
#      +-----------------+
#   /->|                 |--+->(f)--> known keystream
#   |  +-----------------+  |   ^
#   |     |   |    |        |   |
#   \-----+---+----+--------/   \---- known a, b
#
# f does not uniquely determine c, given a, b, and f.  We'll use a solver to
# reverse the keystream until the contents have been determined.

reg0 = LFSR(REG0_SIZE, REG0_TAPS, key0)
reg1 = LFSR(REG1_SIZE, REG1_TAPS, key1)

solver = Solver()
key2 = BitVec("key2", REG2_SIZE)
reg2 = key2

for i in range(8 * known - 1, -1, -1):
    f = (keystream >> i) & 1
    a, b = reg0.step(), reg1.step()

    c = BitVec(f"c{i}", 1)
    lsb = Extract(0, 0, reg2)

    solver.add(lsb == c)
    solver.add(f == a & b | a & c | b & c)

    reg2 = LShR(reg2, 1)
    reg2 ^= If(lsb == 1, REG2_TAPS, BitVecVal(0, REG2_SIZE))

solver.check()
model = solver.model()
key2 = model.eval(key2).as_long()

key = (
    reverse_bits(31, key2) << 36 | reverse_bits(19, key1) << 17 | reverse_bits(17, key0)
)
print(f"recovered key: {key:018x}")

cipher = Cipher(key)
flag = cipher.encrypt(ciphertext)

print("recovered flag:", flag)
