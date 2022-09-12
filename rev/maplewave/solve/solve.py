import numpy as np
import scipy
import sounddevice as sd
import sys
import struct
from bitarray import bitarray
from bitarray.util import ba2int


class Maplewave:
    FRAME = 128

    def __init__(self):
        pass

    def load(self, path):
        with open(path, "rb") as f:
            self.buf = f.read()
        assert self.buf[0:8] == b"MPLEWAVE"

        self.codec, self.frames = struct.unpack("bxxxi", self.buf[8:16])

        self.bits = bitarray()
        self.bits.frombytes(self.buf[16:])
        self.p = 0

    def decode(self):
        match self.codec:
            case 0:
                return np.frombuffer(self.buf[16:], dtype=np.uint8)
            case 1:
                return self.decode_golomb()
            case 2:
                return self.decode_dct()

    def play(self):
        samples = self.decode()
        sd.play(samples, samplerate=16000, blocking=True)

    def decode_golomb(self):
        samples = []

        prev = 0
        prev_diff = 0

        for i in range(self.frames):
            samples.append(np.uint8(np.cumsum(self.decode_rle(Maplewave.FRAME))))
        return np.concatenate(samples, dtype=np.uint8)

    def decode_dct(self):
        samples = []

        dc = 0

        for i in range(self.frames):
            dc += self.decode_golomb_s()
            ac = self.decode_rle(Maplewave.FRAME - 1)

            block = scipy.fft.idct(np.append(dc, ac))
            block = np.uint8(np.clip(block * 128 + 128, 0, 256))
            samples.append(block)

        return np.concatenate(samples)

    def decode_rle(self, total):
        r = []
        i = 0
        prev = 0
        while i < total:
            x = self.decode_golomb_s()
            if x == "rle":
                n = self.decode_golomb_u()
                r += [prev] * n
                i += n
            else:
                r.append(x)
                prev = x
                i += 1
        return np.array(r)

    def decode_golomb_u(self):
        exp = 0
        while self.bits[self.p]:
            exp += 1
            self.p += 1
        self.p += 1

        mantissa = ba2int(self.bits[self.p : self.p + exp - 1]) if exp > 1 else 0
        self.p += exp - 1 if exp > 0 else 0
        x = mantissa | 1 << (exp - 1) if exp > 0 else 0

        return x

    def decode_golomb_s(self):
        sign = self.bits[self.p]
        self.p += 1
        x = self.decode_golomb_u()
        x = -x if sign else x
        if sign and x == 0:
            return "rle"
        return x


mw = Maplewave()
mw.load(sys.argv[1])
mw.play()
