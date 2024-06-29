from sage.all import *
from Crypto.Hash import keccak

class Group:
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    a = 0x0000000000000000000000000000000000000000000000000000000000000000
    b = 0x0000000000000000000000000000000000000000000000000000000000000007
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

    Fp = GF(p)
    Fn = GF(n)

    E = EllipticCurve(Fp, [a, b])
    E.set_order(n)

    G = E(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

    def __init__(self):
        pass

    def generator(self):
        return self.G

    def random_scalar(self):
        return self.Fn(randrange(1, self.n))
    
    def encode_point(self, P) -> bytes:
        if P == 0:
            x, y, z = 0, 1, 0
        else:
            x, y = P.xy()
            z = 1
        return int(x).to_bytes(256//8, 'big') + int(y).to_bytes(256//8, 'big') + int(z).to_bytes(1, 'big')
    
    def encode(self, input) -> bytes:
        if isinstance(input, type(self.G)):
            return self.encode_point(input)
        if isinstance(input, bytes):
            return input
        if isinstance(input, int):
            return input.to_bytes(256//8, 'big')
        raise ValueError(f"Encoding of type {type(input)} does not support!")

    def hash_to_bytes(self, input) -> bytes:
        H = keccak.new(digest_bits=256)
        H.update(self.encode(input))
        return H.digest()
    
    def hash_to_scalar(self, input):
        b = self.hash_to_bytes(input)
        return self.Fn(int.from_bytes(b, 'big'))