from gmpy2 import mpz # speedup operations for testing
#from sage.all import *
FLAG = b"maple{th3_3dw4rd_cu12ve_and_kn0wn_bits_dlp}"

P = 2 ** 414 - 17
d = 3617 

# Implementation of Edwards Curve41417
# x ** 2 + y ** 2 = 1 + 3617 * x ** 2 * y ** 2
# Formulas from http://hyperelliptic.org/EFD/g1p/auto-edwards.html
def on_curve(p):
    x, y = p
    return (x * x + y * y) % P == (1 + 3617 * x * x * y * y) % P

def inv(x):
    return pow(x, -1, P)

def add(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    x = (x1 * y2 + y1 * x2) * inv(1 + d * x1 * x2 * y1 * y2)
    y = (y1 * y2 - x1 * x2) * inv(1 - d * x1 * x2 * y1 * y2)
    return (x % P, y % P)


def mul(x: int, base):
    ans = (0,1)
    cur = base
    while x > 0:
        if x & 1:
            ans = add(cur, ans)
        x >>= 1
        cur = add(cur, cur)
    return ans

base = (17319886477121189177719202498822615443556957307604340815256226171904769976866975908866528699294134494857887698432266169206165, 34)
order = 2 ** 411 - 33364140863755142520810177694098385178984727200411208589594759
assert(on_curve(base))

msg = int.from_bytes(FLAG, 'big')
assert(msg < 2 ** 410)
enc = mul(pow(msg, -1, order), base)
print(f"{enc = }")

ex = 22
sqex = 12
# Have a hint!
bm = (1 << 412) - 1
bm ^= ((1 << ex) -1) << 313
bm ^= ((1 << ex) -1) << 13
bm ^= 1 << 196
hint = bm & pow(msg, -1, order)
print(f"{hint = }")
print(bin(hint))
'''
enc = (29389900956614406804195679733048238721927197300216785144586024378999988819550861039522005309555174206184334563744077143526515, 35393890305755889860162885313105764163711685229222879079392595581125504924571957049674311023316022028491019878405896203357959)
hint = 323811241263249292936728039512527915123919581362694022248295847200852329370976362254362732891461683020125008591836401372097
'''
secret0 = pow(msg, -1, order) & (1<<196)
secret1 = (pow(msg, -1, order) & ((1 << ex) -1) << 313) >> 313
secret2 = (pow(msg, -1, order) &((1 << ex) -1) << 13) >> 13
print(f"{secret0 = }")
print(f"{secret1 = }")
print(f"{secret2 = }")

base = (mpz(base[0]), mpz(base[1]))
print("start table")
dic = {}
tim = 0
A = mul(mpz((2**sqex)*(2**313)), base)
B = mul(mpz((2**sqex)*(2**13)), base)
for c in range(2):
    CC = mul(mpz(hint + c*(2**196)), base)
    AC = CC
    for a in range(0, 2**ex+1, 2**sqex):
        BC = AC
        for b in range(0, 2**ex+1, 2**sqex):
            tim = tim+1
            if (tim%10000==0): print(tim, " out of ", 2*(2**ex//(2**sqex))**2, end='\r')
            dic[BC] = (c * (2**sqex+1) * (2**sqex+1) + a*(2**sqex+1) + b)
            BC = add(BC, B)
        AC = add(AC, A)
print("\ndone table")

A = mul(mpz(1*(2**313)), base)
B = mul(mpz(1*(2**13)), base)
astart = 2199
bstart = 28
for c in range(0,2):
    CC = add(enc, mul(c, base))
    AC = CC
    for a in range(0, 2**sqex+1):
        BC = AC
        for b in range(0, 2**sqex+1):
            tim = tim+1
            if (tim%10000==0): print(tim, "out of ", 2*((2**sqex)**2), end='\r')
            if BC in dic:
                print("\nFOUND!")
                print(a, b)
                exit(0)
            BC = add(BC, B)
        AC = add(AC, A)


# code for generating nonsense 
'''
msg = "Hi! This is a Lorem Ipsum is my middle. Ha ha. As you can see I'm just looking for words to fill this block of text. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum lacinia finibus orci, in sodales justo volutpat sed. Etiam elit odio, mattis eu mi nec, imperdiet rhoncus arcu. Maecenas eu felis in dui laoreet rhoncus tempus et quam. Mauris eleifend sagittis ex. Hope you enjoy the challenge!"
print(412 - len(msg))
msg = list(msg)
for i in range(313, 313+30): msg[i] = '0'
for i in range(13, 13+30): msg[i] = '0'
for i in range(196,197): msg[i] = '0'
print("".join(msg))
'''
