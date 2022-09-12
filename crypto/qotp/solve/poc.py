from random import uniform
from math import sin, cos, tan, pi
from signal import alarm
from Crypto.Util.number import long_to_bytes 

EPS = 1e-9

class Qstate:
    def __init__(self, x: float, y: float):
        assert(abs(x * x + y * y - 1.0) < EPS)
        self.x = x
        self.y = y

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y


class Base:
    def __init__(self, q1: Qstate, q2: Qstate):
        assert(abs(q1 * q2) < EPS)
        self.q1 = q1
        self.q2 = q2

    def measure(self, q: Qstate):
        alpha = (self.q1 * q)**2
        return int(uniform(0, 1) >= alpha)


def get_random_bases(n: int):
    angles = [pi / 4 * uniform(-pi, pi) + pi / 4 for _ in range(n)]
    bases = [Base(Qstate(cos(angle), sin(angle)), Qstate(-sin(angle), cos(angle))) for angle in angles]
    return bases


def binify(s: str):
    return ''.join(format(ord(c), '08b') for c in s)

def decode(enc, bases):
    return ''.join(str(b.measure(q)) for q, b in zip(enc, bases))

def encode(msg, bases):
    enc = [b.q1 if x == '0' else b.q2 for x, b in zip(msg, bases)]
    assert decode(enc, bases) == msg
    return enc


_FLAG = "maple{ru1n3d_BY_th0SE_d412n_r0t4ti0Ns_4ga1N}"
FLAG = "maple{ru1n3d_BY_th0SE_d412n_r0t4ti0Ns_4ga1N}"
FLAG = binify(FLAG)
SMP = 1001
cnt = [0 for _ in range(len(FLAG))]

for _ in range(SMP):
    enc = encode(FLAG, get_random_bases(len(FLAG)))
    angle = - pi / 4
    bases = [Base(Qstate(cos(angle), sin(angle)), Qstate(-sin(angle), cos(angle)))] * len(FLAG)
    for i, b in enumerate(decode(enc, bases)):
        if b == '1':
            cnt[i] += 1
dec = "".join('1' if x > SMP//2 else '0' for x in cnt)
ans = long_to_bytes(int(dec,2))
print(ans)
assert ans.decode() == _FLAG
print("the convincingness of this solution is: ", min([abs(x-SMP//2) for x in cnt]))
