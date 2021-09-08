from utils import sha512, increment_seed, SimulatedCurves, VerifiableCurve, embedding_degree
from sage.all import ZZ, GF, EllipticCurve


class RandomEC(VerifiableCurve):
    def __init__(self, seed, bits, cofactor_bound=8, cofactor_div=2):
        p = self.random_prime(seed, bits)
        super().__init__(seed, p, cofactor_bound, cofactor_div)
        self._bits = bits
        self._standard = "random"
        self._category = "random"

    def set_ab(self):
        self._a = self._field(sha512(self._seed))
        self._b = self._field(sha512(sha512(self._seed)))

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def security(self):
        self._secure = False
        if self._p.nbits()!=self._bits:
            return
        try:
            cardinality = EllipticCurve(GF(self._p), [self._a, self._b]).__pari__().ellsea(self._cofactor_div)
        except ArithmeticError:
            return
        cardinality = ZZ(cardinality)
        if cardinality == 0:
            return
        self._cardinality = cardinality
        if self._cardinality in [self._p + 1, self._p]:
            return
        self._cofactor = ZZ(1)
        self._order = cardinality
        while self._order % 2 == 0:
            self._cofactor *= 2
            self._order //= 2
        if self._cofactor > self._cofactor_bound or not self._order.is_prime():
            return

        self._embedding_degree = embedding_degree(prime=self._p, order=self._order)
        if not (self._order - 1) / self._embedding_degree < 100:
            return
        d = ((self._p + 1 - cardinality) ** 2 - 4 * self._p)
        if d.nbits() <= 100:
            return
        self._secure = True

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.compute_properties()

    @staticmethod
    def random_prime(seed, bits):
        p = ZZ(sha512(seed)) >> (512 - bits)
        return p.next_prime()


def generate_random_curves(count, bits, seed, cofactor_bound=8, cofactor_div=2):
    simulated_curves = SimulatedCurves("random", bits, seed, count)
    curve = RandomEC(seed, bits)
    for _ in range(count):
        if not curve.secure():
            curve.seed_update()
            continue
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        curve = RandomEC(curve.seed(), bits)
        curve.seed_update()
    return simulated_curves
