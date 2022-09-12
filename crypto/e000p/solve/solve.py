from gmpy2 import mpz # speedup operations for testing
from Crypto.Util.number import long_to_bytes

P = 2 ** 414 - 17
d = 3617 

# Implementation of Edwards Curve41417
# x ** 2 + y ** 2 = 1 + 3617 * x ** 2 * y ** 2
# Formulas from http://hyperelliptic.org/EFD/g1p/auto-edwards.html
def on_curve(p):
    x, y = p
    return (x * x + y * y) % P == (1 + d * x * x * y * y) % P

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

'''
msg = int.from_bytes(FLAG, 'big')
assert(msg < 2 ** 410)
enc = mul(pow(msg, -1, order), base)
print(f"{enc = }")

# Have a hint!
bm = (1 << 412) - 1
bm ^= ((1 << ex) -1) << 313
bm ^= ((1 << ex) -1) << 13
bm ^= 1 << 196
hint = bm & pow(msg, -1, order)
print(f"{hint = }")
'''
ex = 22
sqex = 12
enc = (29389900956614406804195679733048238721927197300216785144586024378999988819550861039522005309555174206184334563744077143526515, 35393890305755889860162885313105764163711685229222879079392595581125504924571957049674311023316022028491019878405896203357959)
hint = 323811241263249292936728039512527915123919581362694022248295847200852329370976362254362732891461683020125008591836401372097
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
            dic[BC] = (a,b,c)
            BC = add(BC, B)
        AC = add(AC, A)
print("\ndone table")

A = mul(mpz(1*(2**313)), base)
B = mul(mpz(1*(2**13)), base)
a_ans = 2199
b_ans = 28
c_ans = 0
for c in range(2):
    if a_ans != 0: break # end early for testing, brute force takes a bit
    CC = add(enc, mul(c*(2**196), base))
    AC = CC
    for a in range(0, 2**sqex+1):
        if a_ans != 0: break 
        BC = AC
        for b in range(0, 2**sqex+1):
            if a_ans != 0: break 
            tim = tim+1
            if (tim%10000==0): print(tim, "out of ", 2*((2**sqex)**2), end='\r')
            if BC in dic:
                print("\nFOUND!")
                a_ans = a
                b_ans = b
                c_ans = c
                break
            BC = add(BC, B)
        AC = add(AC, A)

q = add(enc, mul(c_ans*(2**196) + a_ans*(2**313) + b_ans*(2**13), base))
assert q in dic

a, b, c = dic[q]
inv = hint + (a-a_ans)*(2**313) + (b-b_ans)*(2**13)
print(long_to_bytes(pow(inv,-1, order)))

