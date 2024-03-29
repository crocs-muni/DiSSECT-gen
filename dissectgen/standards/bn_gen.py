""" This is an implementation of an algorithm for generation of Barreto-Naehrig curves based on the ISO/IEC
15946-5 standard (part 7.3).

Changes compared to the ISO standard:
- the algorithm skips the step (e)
- we take as an input seed (parameter u in the standard) instead of the size of the desired field,
but the transformation between u and the size is trivial (step (b)).
- we extend the algorithm to generate as many curves as desired by taking larger values of u (not just the smallest)."""

from sage.all import ZZ, PolynomialRing, EllipticCurve, GF, sqrt
from dissectgen.standards.utils import VerifiableCurve, SimulatedCurves, seed_update, curve_command_line


class BNFail(Exception):
    pass


# ISO standard
class BN(VerifiableCurve):
    def __init__(self, seed):
        super().__init__(seed, None, None, None)
        x = ZZ(seed)
        self._bits = (36 * x ** 4 + 36 * x ** 3 + 24 * x ** 2 + 6 * x + 1).nbits()
        self._standard = "bn"
        self._category = "bn"

    def set_ab(self):
        pass

    def generate_generator(self):
        self._a = 0
        b = 0
        F = GF(self._p)
        G = None
        while True:
            b += 1
            if not F(b + 1).is_square():
                continue
            E = EllipticCurve(F, [0, b])
            y0 = sqrt(F(b + 1))
            G = E(1, y0)
            if self._order * G == E(0):
                break
        self._b = b
        self._generator = G[0], G[1]

    def security(self):
        self._secure = False
        u = ZZ(self._seed)
        x = PolynomialRing(ZZ, 'x').gen()
        P = 36 * x ** 4 + 36 * x ** 3 + 24 * x ** 2 + 6 * x + 1

        t = 6 * u ** 2 + 1
        p = P(-u)
        if p.nbits() != self._bits:
            raise BNFail
        n = p + 1 - t
        if not n.is_prime() or not p.is_prime():
            p = P(u)
            if p.nbits() != self._bits:
                raise BNFail
            n = p + 1 - t
            if not n.is_prime() or not p.is_prime():
                return False
            self._seed = hex(-u)
        """
        Skipped step (e), see the info above.
        for d in divisors(n - 1):
            if log(n, 2) ** 2 < d < sqrt(n):
                return False
        for e in divisors(n + 1):
            if log(n, 2) ** 2 < e < sqrt(n):
                return False
        """
        self._p = p
        self._cardinality = n
        self._order = n
        self._secure = True
        self._cofactor = ZZ(1)

    def seed_update(self, offset=1):
        self._seed = seed_update(self._standard, self._seed, offset)
        self.clear()

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.generate_generator()
        self.compute_properties()


def generate_bn_curves(attempts, seed, count=0):
    x = ZZ(seed)
    bits = (36 * x ** 4 + 36 * x ** 3 + 24 * x ** 2 + 6 * x + 1).nbits()
    simulated_curves = SimulatedCurves("bn", bits, seed, attempts)
    curve = BN(seed)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        try:
            if not curve.secure():
                curve.seed_update()
                continue
        except BNFail:
            print("no more BN curves of this bitlength")
            break
        curve.generate_generator()
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        c += 1
        curve = BN(curve.seed())
        curve.seed_update()
    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_bn_curves(args.attempts, args.seed, args.count)
    results.to_json_file(args.outfile)
