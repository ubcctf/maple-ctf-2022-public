

from pydoc import plain
from utils import *
import random


INV_SBOX = [SBOX.index(i) for i in range(255)]
INV_SPIRAL = [
    [92, 218, 173, 241],
    [24, 21, 217, 233],
    [54, 142, 124, 192],
    [235, 48, 127, 201],
]

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

        for i in range(1, self.rounds):
            self.substitute()
            self.rotate()
            self.mix()
            self.add_key(i)

        self.substitute()
        self.rotate()
        self.add_key(self.rounds)

        return matrix2bytes(self.state)

    def add_key(self, idx):
        for i in range(4):
            for j in range(4):
                self.state[i][j] = (self.state[i][j] + self.keys[idx][i][j]) % 255

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
                out[i][j] %= 255

        self.state = out

    def decrypt(self, ciphertext):
        plaintext = b""
        for i in range(0, len(ciphertext), 16):
            plaintext += self.decrypt_block(ciphertext[i : i + 16])
        return plaintext

    def decrypt_block(self, ciphertext):
        self.state = bytes2matrix(ciphertext)
        self.inv_add_key(self.rounds)
        self.inv_rotate()
        self.inv_substitute()

        for i in range(self.rounds-1, 0, -1):
            self.inv_add_key(i)
            self.inv_mix()
            self.inv_rotate()
            self.inv_substitute()

        self.inv_add_key(0)

        return matrix2bytes(self.state)

    def inv_add_key(self, idx):
        for i in range(4):
            for j in range(4):
                self.state[i][j] = (self.state[i][j] - self.keys[idx][i][j]) % 255

    def inv_substitute(self):
        for i in range(4):
            for j in range(4):
                self.state[i][j] = INV_SBOX[self.state[i][j]]

    def inv_rotate(self):
        self.state = spiralLeft(self.state)

    def inv_mix(self):
        out = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    out[i][j] += INV_SPIRAL[i][k] * self.state[k][j]
                out[i][j] %= 255

        self.state = out

FLAG = b'maple{this_is_a_test_flag}'
import string
answer = ''.join([random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase) for i in range(16)])
cipher = Spiral(answer.encode(), rounds=4)

print("Key:", answer)
enc_flag = cipher.encrypt(FLAG)
key = []


# recover key
for pos in range(16):
    possible = set([i for i in range(255)])

    while len(possible) > 1:
        plaintexts = []
        ciphertexts = []

        pt = [i for i in range(16)]
        random.shuffle(pt)
        for i in range(255):
            pt[pos] = i
            ct = cipher.encrypt(pt)
            plaintexts.append(pt)
            ciphertexts.append(ct)


        correct = set()
        for keyGuess in range(255):
            total = 0
            for pt, ct in zip(plaintexts, ciphertexts):
                byte = (ct[pos] - keyGuess) % 255
                byte = INV_SBOX[byte]

                total += byte

            if total % 255 == 0:
                correct.add(keyGuess)

    
        possible = possible.intersection(correct)

    assert len(possible) == 1
    key.append(possible.pop())

print(bytes(key))
s = Spiral(key, rounds=4)
dec = s.decrypt(enc_flag)

print(dec)