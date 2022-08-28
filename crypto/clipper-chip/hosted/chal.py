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


print(
    """Welcome to the MB9001C67 encryption service.
We'll do your encryption in hardware for maximum security."""
)

while True:
    try:
        key = int(input("key (hex, most significant bit loaded into chip first): "), 16)
        pt = bytes.fromhex(
            input(
                "plaintext or ciphertext (hex, most significant bit of each byte encrypted first): "
            )
        )
        cipher = Cipher(key)
        ct = cipher.encrypt(pt)
        print("ciphertext:", ct.hex())
    except:
        print("Invalid input.")
