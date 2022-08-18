""" Implementation of the SEC standard, see section 3.1.1.1 in
    https://www.secg.org/sec1-v1.pdf
"""

from dissectgen.standards.utils import sha1, generate_curves, curve_command_line
from dissectgen.standards.x962_gen import X962
from sage.all import ZZ, floor, GF, Integer, EllipticCurve


def large_prime_factor(m: ZZ, bound: int):
    """Tests if the size of the largest prime divisor of m is upper-bounded by bound"""
    h, prime = Integer(1), Integer(2)
    tmp = m
    while h < bound and prime < bound:
        if tmp % prime == 0:
            h *= prime
            tmp = tmp // prime
            continue
        prime = prime.next_prime()
    if h >= bound:
        return False
    if tmp.is_prime():
        return h
    return False


class SECG(X962):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self._cofactor_bound = ZZ(4)
        self._standard = "secg"
        self._category = "secg"
        self._embedding_degree_bound = 100

    def order_check(self):
        try:
            cardinality = EllipticCurve(GF(self._p), [self._a, self._b]).__pari__().ellsea(self._cofactor_div)
        except ArithmeticError:
            return False
        cardinality = Integer(cardinality)
        if cardinality == 0:
            return False
        cofactor = large_prime_factor(cardinality, self._cofactor_bound)
        self._cardinality = cardinality
        if not cofactor:
            return False
        self._order, self._cofactor = cardinality // cofactor, cofactor
        return True

    def security(self):
        super().security()
        if not self._secure:
            return
        n_1_bound = floor(self._order ** (1 - 19 / 20))
        if not (large_prime_factor(self._order - 1, n_1_bound) and large_prime_factor(self._order + 1, n_1_bound)):
            return
        self._secure = True

    def generate_generator(self):
        c = 1
        while True:
            r = bytes("Base point", 'ASCII') + bytes([1]) + bytes([c]) + bytes.fromhex(self._seed[2:])
            e = ZZ(sha1(r.hex()))
            t = e % (2 * self._p)
            x, z = t % self._p, t // self._p
            c += 1
            try:
                y = self.curve().lift_x(x)[1]
            except ValueError:
                continue
            if Integer(y) % 2 == z:
                return self.curve()(x, y) * self._cofactor


def generate_secg_curves(attempts, p, seed, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curve = SECG(seed, p)
    return generate_curves(attempts, count, curve)


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_secg_curves(args.attempts, args.prime, args.seed, args.count)
    results.to_json_file(args.outfile)
