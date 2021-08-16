from utils import embedding_degree, increment_seed, VerifiableCurve, SimulatedCurves
from sage.all import ZZ, EllipticCurve, GF


class NUMS(VerifiableCurve):
    def __init__(self, seed, p):
        super().__init__(seed, p, cofactor_bound=1, cofactor_div=1)
        self._standard = "nums"
        self._category = "nums"
        self._cofactor = 1

    def set_ab(self):
        self._b = ZZ(self._seed)
        self._a = ZZ(self._p - 3)

    def security(self):
        self._secure = False
        try:
            cardinality = EllipticCurve(GF(self._p), [-3, self._b]).__pari__().ellsea(1)
        except ArithmeticError:
            return 
        cardinality = ZZ(cardinality)
        if cardinality == 0:
            return
        if not cardinality.is_prime():
            return
        twist_card = 2 * (self._p + 1) - cardinality

        if self._p <= cardinality:
            self._b = self._p - self._b
            cardinality = twist_card

        if not twist_card.is_prime():
            return

        self._embedding_degree = embedding_degree(prime=self._p, order=cardinality)
        if not (cardinality - 1) / self._embedding_degree < 100:
            return
        d = ((self._p + 1 - cardinality) ** 2 - 4 * self._p)
        if d.nbits() <= 100:
            return
        self._cardinality = cardinality
        self._order = cardinality
        self._secure = True

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.compute_properties()


def generate_nums_curves(count, p, seed):
    """Generates at most #count curves according to the standard
    """
    simulated_curves = SimulatedCurves("nums", p.nbits(), seed, count)
    curve = NUMS(seed, p)
    for _ in range(count):
        if not curve.secure():
            curve.seed_update()
            continue
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        curve = NUMS(curve.seed(), p)
        curve.seed_update()
    return simulated_curves
