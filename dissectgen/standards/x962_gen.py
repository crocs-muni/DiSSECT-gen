from dissectgen.standards.utils import increment_seed, embedding_degree, SimulatedCurves, VerifiableCurve, find_integer, get_b_from_r, curve_command_line
from sage.all import ZZ, GF, EllipticCurve, prime_range, is_pseudoprime, sqrt


def verify_near_primality(u: ZZ, r_min: ZZ, l_max=255, cofactor_bound=None) -> dict:
    """Verifying near primality according to the standard"""
    n = u
    h = 1
    for prime in prime_range(l_max):
        while n % prime == 0:
            n = ZZ(n / prime)
            h = h * prime
            if cofactor_bound is not None and h > cofactor_bound:
                return {}
            if n < r_min:
                return {}
    if n < r_min:
        return {}
    if is_pseudoprime(n):
        return {'cofactor': h, 'order': n}
    return {}


class X962(VerifiableCurve):
    def __init__(self, seed, p, cofactor_bound=None, cofactor_div=0):
        super().__init__(seed, p, cofactor_bound, cofactor_div)
        self._standard = "x962"
        self._category = "x962"
        self._embedding_degree_bound = 20
        self._rmin = None

    def coefficients_check(self):
        if self._b is None or (4 * self._a ** 3 + 27 * self._b ** 2) % self._p == 0:
            return False

    def order_check(self):
        try:
            cardinality = EllipticCurve(GF(self._p), [self._a, self._b]).__pari__().ellsea(self._cofactor_div)
        except ArithmeticError:
            return False
        self._cardinality = ZZ(cardinality)
        if self._cardinality == 0:
            return False
        # a somewhat arbitrary bound (more strict than in the standard), but it will speed up the generation process
        r_min_bits = self._cardinality.nbits() - 5
        r_min = max(2 ** r_min_bits, 4 * sqrt(self._p)) if self._rmin is None else self._rmin
        curve = verify_near_primality(self._cardinality, r_min, cofactor_bound=self._cofactor_bound)
        if not curve:
            return False
        self._order, self._cofactor = curve['order'], curve['cofactor']
        return True

    def security(self):
        self._secure = self.coefficients_check()
        if not self.order_check():
            return
        self._embedding_degree = embedding_degree(self._p, self._order)
        if self._embedding_degree < self._embedding_degree_bound:
            return
        if self._p == self._cardinality:
            return
        self._secure = True

    def set_ab(self):
        r = find_integer(self._seed, self._p.nbits())
        b = get_b_from_r(r, self._p)
        if b is None:
            return
        self._b = ZZ(min(b, self._p - b))
        self._a = ZZ(self._p - 3)

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def find_curve(self):
        while not self.secure():
            self.seed_update()
        self.compute_properties()


def generate_x962_curves(attempts, p, seed, cofactor_bound=None, cofactor_div=0, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    if cofactor_bound is not None:
        cofactor_bound = ZZ(cofactor_bound)
    simulated_curves = SimulatedCurves("x962", p.nbits(), seed, attempts)
    curve = X962(seed, p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if not curve.secure():
            curve.seed_update()
            continue
        curve.compute_properties()
        simulated_curves.add_curve(curve)
        c += 1
        curve = X962(curve.seed(), p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
        curve.seed_update()
    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_x962_curves(args.attempts, args.prime, args.seed, args.cofactor_bound, args.cofactor_div,
                                   args.count)
    results.to_json_file(args.outfile)
