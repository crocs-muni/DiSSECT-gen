""" Implementation of the SEC standard, see
    https://www.secg.org/sec2-v2.pdf
    https://www.secg.org/sec1-v2.pdf
"""

from utils import sha1, SimulatedCurves, curve_command_line
from x962_gen import X962
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
    def __init__(self, seed, p, cofactor_bound=4, cofactor_div=2):
        super().__init__(seed, p, cofactor_bound, cofactor_div)
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
        """Returns generator as specified in SEC, currently not using"""
        c = 1
        while True:
            r = bytes("Base point", 'ASCII') + bytes([1]) + bytes([c]) + bytes.fromhex(seed)
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


def generate_secg_curves(attempts, p, seed, cofactor_bound=4, cofactor_div=2, count=0):
    """This is an implementation of the SEC standard suitable for large-scale simulations
    """
    simulated_curves = SimulatedCurves("secg", p.nbits(), seed, attempts)
    curve = SECG(seed, p, cofactor_bound=cofactor_bound, cofactor_div=cofactor_div)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if not curve.secure():
            curve.seed_update()
            continue
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        c += 1
        curve = SECG(curve.seed(), p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
        curve.seed_update()
    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_secg_curves(args.attempts, args.prime, args.seed, args.cofactor_bound, args.cofactor_div,
                                   args.count)
    results.to_json_file(args.outfile)
