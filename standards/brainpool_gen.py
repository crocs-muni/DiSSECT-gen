"""Implementation of the Brainpool standard, see
    https://tools.ietf.org/pdf/rfc5639.pdf#15
"""
from sage.all import ZZ, GF, EllipticCurve
from utils import increment_seed, embedding_degree, find_integer, SimulatedCurves, VerifiableCurve, \
    class_number_check, curve_command_line

CHECK_CLASS_NUMBER = False


def gen_brainpool_prime(seed: str, nbits: int) -> ZZ:
    """Generates a prime of length nbits out of 160bit seed s"""
    while True:
        p = find_integer(seed, nbits, brainpool_prime=True)
        while not (p % 4 == 3 and p.is_prime()):
            p += 1
        if p.nbits() == nbits:
            return p
        seed = increment_seed(seed)


class Brainpool(VerifiableCurve):
    def __init__(self, seed, p):
        super().__init__(seed, p, cofactor_bound=1, cofactor_div=1)
        self._standard = "brainpool"
        self._category = "brainpool"
        self._cofactor = 1
        self._original_seed = seed

    def security(self):
        self._secure = False
        try:
            curve = EllipticCurve(GF(self._p), [self._a, self._b])
        except ArithmeticError:
            return
        order = curve.__pari__().ellsea(1)
        if order == 0:
            return
        order = ZZ(order)
        if order >= self._p:
            return
        if not order.is_prime():
            return
        self._embedding_degree = embedding_degree(prime=self._p, order=order)
        if not (order - 1) / self._embedding_degree < 100:
            return
        if CHECK_CLASS_NUMBER and not class_number_check(curve, order, 10 ** 7):
            return
        self._cardinality = order
        self._order = order
        self._secure = True

    def set_ab(self):
        pass

    def set_a(self):
        self._a = find_integer(self._seed, self._bits)

    def check_a(self):
        if self._a is None:
            return False
        try:
            c = -3 * self._field(self._a) ** (-1)
            c.nth_root(4)
            return True
        except ValueError:
            return False

    def set_b(self, b_seed=None):
        if b_seed is None:
            b_seed = self._seed
        self._b = find_integer(b_seed, self._bits)

    def check_b(self):
        return self._b is not None and not self._field(self._b).is_square()

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed)

    def set_seed(self, seed):
        self._seed = seed

    def generate_generator(self, seed=None):
        """Finds generator of curve as scalar*P where P has smallest x-coordinate"""
        if seed is None:
            seed = self._seed
        scalar = find_integer(increment_seed(seed), self._bits)
        x = None
        for x in self._field:
            if (x ** 3 + self._a * x + self._b).is_square():
                break
        y = (x ** 3 + self._a * x + self._b).sqrt()
        y = ZZ(min(y, self._p - y))
        point = scalar * self.curve()(x, y)
        self._generator = point[0], point[1]

    def find_curve(self):
        """Generates one Brainpool curve over F_p (number of bits of p is nbits) out of 160bit seed"""
        self.set_a()
        while True:
            while not self.check_a():
                self.seed_update()
                self.set_a()
            self.seed_update()
            self.set_b()
            while not self.check_b():
                self.seed_update()
                self.set_b()
            if not self.secure():
                self.seed_update()
                continue
            self.generate_generator()
            break


def generate_brainpool_curves(attempts: int, p: ZZ, initial_seed: str, count=0) -> SimulatedCurves:
    """This is an implementation of the Brainpool standard suitable for large-scale simulations
        For more readable implementation, see 'brainpool_curve' above
    """
    simulated_curves = SimulatedCurves("brainpool", p.nbits(), initial_seed, attempts)
    curve = Brainpool(initial_seed, p)
    b_seed = None
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if curve.not_defined():
            curve.set_a()
            if not curve.check_a():
                curve.seed_update()
                curve.clear()
                continue
            b_seed = increment_seed(curve.seed())
        curve.set_b(b_seed)
        if not curve.check_b():
            b_seed = increment_seed(b_seed)
            continue
        if not curve.secure():
            curve.set_seed(increment_seed(b_seed))
            curve.clear()
            continue
        curve.generate_generator(b_seed)
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        c += 1
        curve = Brainpool(curve.seed(), p)
        curve.seed_update()

    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_brainpool_curves(args.attempts, args.prime, args.seed, args.count)
    results.to_json_file(args.outfile)
