from sage.all import GF, EllipticCurve, ZZ, PolynomialRing
from dissectgen.standards.utils import VerifiableCurve, SimulatedCurves, seed_update, curve_command_line


class BLS(VerifiableCurve):
    def __init__(self, seed):
        super().__init__(seed, None, None, None)
        self._standard = "bls"
        self._category = "bls"
        self._bits = ZZ(381)

    def set_ab(self):
        pass

    def cm_method(self):
        field = GF(self._p)
        i = field(0)
        r = self._p + 1 - self.trace()
        z = PolynomialRing(field, 'z').gen()
        while True:
            i += 1
            if i.is_square():
                continue
            if not (z ** 3 - i).roots():
                break
        b = ZZ(1)
        while True:
            E = EllipticCurve(field, [0, b])
            P = E.random_point()
            if r * P == E(0) and 2 * self.trace() * P != E(0) and r == E.order():
                break
            b *= i
        self._b = ZZ(b)
        self._a = ZZ(0)

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
        if not q.nbits() == 381 or not q.is_prime() or q == s:
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
        self.cm_method()
        self.generate_generator()
        self.compute_properties()

    def generate_generator(self):
        x = ZZ(1)
        while True:
            try:
                point = self.curve().lift_x(x)
                y = min(point[1], self._p - point[1])
                point = self._cofactor * self.curve()(x, y)
                if point != self.curve()(0):
                    break
            except ValueError:
                pass
            x += 1

        self._generator = point[0], point[1]


def generate_bls_curves(attempts, seed, count=0):
    simulated_curves = SimulatedCurves("bls", 381, seed, attempts)
    curve = BLS(seed)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if not curve.secure():
            curve.seed_update()
            continue
        curve.cm_method()
        curve.compute_properties()
        curve.generate_generator()
        simulated_curves.add_curve(curve)
        c += 1
        curve = BLS(curve.seed())
        curve.seed_update()
    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_bls_curves(args.attempts, args.seed, args.count)
    results.to_json_file(args.outfile)
