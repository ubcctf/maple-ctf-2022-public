

from pydoc import plain
from utils import *
import random


INV_SBOX = [SBOX.index(i) for i in range(256)]
INV_MIX = [[ 35  ,78 , 69, 231],
[ 25 ,131  ,38 , 79],
[ 67 ,194 ,160 ,198],
[ 36 ,109 ,245, 167],]

class Spiral:
    def __init__(self, key, rounds=4):
        self.rounds = rounds
        self.keys = [bytes2matrix(key)]
        self.BLOCK_SIZE = 16

        for i in range(rounds):
            self.keys.append(spiralLeft(self.keys[-1]))

    def encrypt(self, plaintext):
        if len(plaintext) % self.BLOCK_SIZE != 0:
            padding = self.BLOCK_SIZE - len(plaintext) % self.BLOCK_SIZE
            plaintext += bytes([padding] * padding)

        ciphertext = b""
        for i in range(0, len(plaintext), 16):
            ciphertext += self.encrypt_block(plaintext[i : i + 16])
        return ciphertext

    def encrypt_block(self, plaintext):
        self.state = bytes2matrix(plaintext)
        self.add_key(0)

        # for i in range(1, self.rounds):
        self.substitute()
        self.rotate()
        self.mix()
        self.add_key(1)

        self.substitute()
        self.rotate()
        self.mix()
        self.add_key(2)

        self.substitute()
        self.rotate()
        # self.mix()
        # self.add_key(3)

        return matrix2bytes(self.state)

    def add_key(self, idx):
        for i in range(4):
            for j in range(4):
                self.state[i][j] = (self.state[i][j] + self.keys[idx][i][j]) % 256

    def substitute(self):
        for i in range(4):
            for j in range(4):
                self.state[i][j] = SBOX[self.state[i][j]]

    def rotate(self):
        self.state = spiralRight(self.state)

    def mix(self):
        out = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    out[i][j] += SPIRAL[i][k] * self.state[k][j]
                out[i][j] %= 256

        self.state = out


FLAG = b'maple{this_is_a_test_flag}'
import string
answer = ''.join([random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase) for i in range(16)])
cipher = Spiral(answer.encode(), rounds=4)
print(answer)
key = []

# print(cipher.decrypt(cipher.encrypt(FLAG)))


pos = 0
plaintexts = []
ciphertexts = []

pt = [0 for i in range(16)]
random.shuffle(pt)
for i in range(256):
    pt[pos] = i
    ct = cipher.encrypt(pt)
    plaintexts.append(pt)
    ciphertexts.append(ct)

# uniq = set()
total = []
for i in range(256):

    total.append(ciphertexts[i][7])
    # print(ciphertexts[i][2])
    # print(list(ciphertexts[i]))

print(sum(total) % 256, len(set(total)))
    # print(ciphertexts[i][3])



# recover key
for pos in range(16):
    possible = set([i for i in range(256)])

    while len(possible) > 1:
        plaintexts = []
        ciphertexts = []

        pt = [i for i in range(16)]
        random.shuffle(pt)
        for i in range(256):
            pt[pos] = i
            ct = cipher.encrypt(pt)
            plaintexts.append(pt)
            ciphertexts.append(ct)


        correct = set()
        for keyGuess in range(256):
            total = 0
            for pt, ct in zip(plaintexts, ciphertexts):
                byte = (ct[pos] - keyGuess) % 256
                byte = INV_SBOX[byte]

                total += byte

            if total % 256 == 128:
                correct.add(keyGuess)

    
        possible = possible.intersection(correct)

    if len(possible) == 1:
    # print(key)
        key.append(possible.pop())


print(list(b"0123456789abcdef"))
print(key)

print(bytes(key))
# decrypt process (invert the SPIRAL matrice in Z_256)


