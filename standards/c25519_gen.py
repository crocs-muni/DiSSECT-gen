from utils import embedding_degree, increment_seed, VerifiableCurve, SimulatedCurves
from sage.all import ZZ, EllipticCurve, GF


class C25519(VerifiableCurve):
    def __init__(self, seed, p):
        if p % 4 == 1:
            super().__init__(seed, p, cofactor_bound=8, cofactor_div=2)
        else:
            super().__init__(seed, p, cofactor_bound=4, cofactor_div=2)
        self._standard = "c25519"
        self._category = "c25519"

    def set_ab(self):
        """Transformation from Montgomery to Weierstrass"""
        mont_a = ZZ(self._seed)
        assert mont_a > 2 and mont_a % 4 == 2
        mont_a = GF(self._p)(mont_a)
        self._a = 1 - mont_a ** 2 / 3
        self._b = mont_a * (2 * mont_a ** 2 - 9) / 27

    def security(self):
        self._secure = False
        try:
            self._curve = EllipticCurve(GF(self._p), [self._a, self._b])
            cardinality = self._curve.__pari__().ellsea(self._cofactor_div)
        except ArithmeticError:
            return
        cardinality = ZZ(cardinality)
        if cardinality == 0:
            return
        self._cofactor = 8 if self._p % 4 == 1 else 4

        if not ZZ(cardinality / self._cofactor).is_prime():
            return
        order = cardinality // self._cofactor
        twist_card = 2 * (self._p + 1) - cardinality
        if not ZZ(twist_card / 4).is_prime():
            return
        if self._p - cardinality in [-1, 0]:
            return
        self._embedding_degree = embedding_degree(prime=self._p, order=order)
        if not (cardinality - 1) / self._embedding_degree < 100:
            return
        d = (self._p + 1 - cardinality) ** 2 - 4 * self._p
        d = d.squarefree_part()
        self._cm = 4 * d if d % 4 != 1 else d
        if self._cm.nbits() <= 100:
            return
        self._cardinality = cardinality
        self._order = order
        self._secure = True

    def seed_update(self, offset=4):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.compute_properties()

    def generate_generator(self):
        field = GF(self._p)
        u = field(0)
        point = 0, 0
        A = GF(self._p)(self._seed)
        while True:
            u += 1
            v2 = u ** 3 + A * u ** 2 + u
            if not v2.is_square():
                continue
            v = v2.sqrt()
            x, y = u + A / 3, v
            point = self.curve()(x, y)
            infty = self.curve()(0)
            if point != infty and self.order() * point == infty:
                break

        self._generator = point[0], point[1]


def generate_c25519_curves(count, p, seed):
    """Generates at most #count curves according to the standard
    """
    simulated_curves = SimulatedCurves("c25519", p.nbits(), seed, count)
    curve = C25519(seed, p)
    for _ in range(count):
        if not curve.secure():
            curve.seed_update()
            continue
        curve.generate_generator()
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        curve = C25519(curve.seed(), p)
        curve.seed_update()
    return simulated_curves