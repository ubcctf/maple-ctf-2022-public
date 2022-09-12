from base64 import urlsafe_b64decode, urlsafe_b64encode
from fastecdsa.curve import secp256k1
from Crypto.Util.number import inverse, bytes_to_long as bl
from hashlib import sha256

def b64decode(msg: str) -> bytes:
    if len(msg) % 4 != 0:
        msg += "=" * (4 - len(msg) % 4)
    return urlsafe_b64decode(msg.encode())


def b64encode(msg: bytes) -> str:
    return urlsafe_b64encode(msg).decode().rstrip("=")


# login with any username and copy the jwt token
cookie = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWJjZCJ9.75J83TiCMONIDtDLvDQ8FKHa4wx7DNHkauX-Izu11S-wAxbc4z_xrKKBMC3_IS3W0_8JQStEvZw2--CqrKCYig'

print(b64decode(cookie.split('.')[0]), b64decode(cookie.split('.')[1]))
signature = b64decode(cookie.split('.')[2])
r = int.from_bytes(signature[:32], "little")
s = int.from_bytes(signature[32:], "little")


G = secp256k1.G
order = secp256k1.q
msg = b'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWJjZCJ9'
z = sha256(msg).digest()
z = bl(z)

# find the private key
private = inverse((s - r) * inverse(z, order), order)
print(private)


# forge a new token
from jwt import ES256
es = ES256(private)
print(es.sign({"user":"admin"}))

# put new token into cookie => flag