import random
from re import S
sz = 255
import random
SBOX = [i for i in range(sz)]
random.shuffle(SBOX)


while True:
    spirals = []
    while len(spirals) < 16:
        i = random.randint(0, sz)
        if i % 3 != 0 and i % 5 != 0 and i % 17 != 0 and i not in spirals:
            spirals.append(i)

    spirals.sort()
    # spirals = [spirals[i:i+4] for i in range(0, len(spirals), 4)]

    mapping = [0, 1, 2, 3, 11, 12, 13, 4, 10, 15, 14, 5, 9, 8, 7, 6]
    spiral = [spirals[m] for m in mapping]
    spiral = [spiral[i:i+4] for i in range(0, len(spiral), 4)]

    m = Matrix(Integers(255), spiral)

    if m.is_invertible():
        print(m)
        print(1/m)
        break