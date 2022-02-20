from sage.all import ZZ, PolynomialRing, EllipticCurve, GF, sqrt, divisors, log
from utils import VerifiableCurve, SimulatedCurves, seed_update


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


def generate_bn_curves(count, seed):
    x = ZZ(seed)
    bits = (36 * x ** 4 + 36 * x ** 3 + 24 * x ** 2 + 6 * x + 1).nbits()
    simulated_curves = SimulatedCurves("bn", bits, seed, count)
    curve = BN(seed)
    for _ in range(count):
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
        curve = BN(curve.seed())
        curve.seed_update()
    return simulated_curves
