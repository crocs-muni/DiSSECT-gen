from dissectgen.standards.utils import embedding_degree, increment_seed, VerifiableCurve, generate_curves, \
    curve_command_line
from sage.all import ZZ, EllipticCurve, GF


class NUMS(VerifiableCurve):
    def __init__(self, seed, p):
        conditions = {"p": p, "seed": seed, "cofactor_bound": 1, "cofactor_div": 1}
        super().__init__(conditions)
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


def generate_nums_curves(attempts, p, seed, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curve = NUMS(seed, p)
    return generate_curves(attempts, count, curve)


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_nums_curves(args.attempts, args.prime, args.seed, args.count)
    results.to_json_file(args.outfile)

