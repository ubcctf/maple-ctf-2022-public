from utils import *




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