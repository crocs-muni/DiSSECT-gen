import sage.graphs.generators.families
from sage.all import GF, EllipticCurve, ZZ
from utils import VerifiableCurve, SimulatedCurves, seed_update


class BLS(VerifiableCurve):
    def __init__(self, seed):
        super().__init__(seed, None, None, None)
        self._standard = "nums"
        self._category = "nums"

    def set_ab(self):
        pass

    def cm_method(self):
        i = GF(self._p)(0)
        r = self._p + 1 - self.trace()
        while True:
            i += 1
            if i.is_square():
                continue
            try:
                i.nth_root(3)
            except ValueError:
                break
        b = 1
        while True:
            E = EllipticCurve(GF(self._p), [0, b])
            P = E.random_point()
            if r * P == E(0) and 2 * self.trace() * P != E(0) and r == E.order():
                break
            b *= i
        self._b = b
        self._a = 0

    def seed_update(self, offset=1):
        self._seed = seed_update(self._standard, self._seed, offset)
        self._secure = None

    def security(self):
        self._secure = False
        s = ZZ(self._seed)
        q = (s - 1) ** 2 * (s ** 4 - s ** 2 + 1) / 3 + s
        try:
            q = ZZ(q)
        except TypeError:
            return False
        if not q.nbits() == 383 or not q.is_prime() or q == s:
            return False
        r = s ** 4 - s ** 2 + 1
        if not r.nbits() == 255 or not r.is_prime():
            return False
        self._p = q
        self._cardinality = q - s
        self._order = r
        self._secure = True
        self._cofactor = self._cardinality // self._order

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.generate_generator()
        self.compute_properties()

    def generate_generator(self):
        x = 1
        while True:
            try:
                point = self.curve().lift_x(x)
                break
            except ValueError:
                x += 1
        y = min(point[1], self._p - point[1])
        point = self._cofactor * self.curve()(x, y)
        self._generator = point[0], point[1]


def generate_bls_curves(count, seed):
    simulated_curves = SimulatedCurves("bls", 383, seed, count)
    curve = BLS(seed)
    for _ in range(count):
        if not curve.secure():
            curve.seed_update()
            continue
        curve.compute_properties()
        curve.generate_generator()
        simulated_curves.add_curve(curve)
        curve = BLS(curve.seed())
        curve.seed_update()
    return simulated_curves
