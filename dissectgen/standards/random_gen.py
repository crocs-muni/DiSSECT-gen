from dissectgen.standards.utils import sha512, increment_seed, generate_curves, VerifiableCurve, embedding_degree, \
    curve_command_line
from sage.all import ZZ, GF, EllipticCurve


class RandomEC(VerifiableCurve):
    def __init__(self, seed, bits, cofactor_bound=8, cofactor_div=2):
        p = self.random_prime(seed, bits)
        conditions = {"seed": seed, "p": p, "cofactor_bound": cofactor_bound, "cofactor_div": cofactor_div}
        super().__init__(conditions)
        self._bits = bits
        self._standard = "random"
        self._category = "random"
        self._original_seed = seed

    def set_ab(self):
        self._a = self._field(sha512(self._seed))
        self._b = self._field(sha512(sha512(self._seed)))

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def security(self):
        self._secure = False
        if self._p.nbits() != self._bits:
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
        self._seed = self._original_seed
        self._secure = True

    @staticmethod
    def random_prime(seed, bits):
        hash = ZZ(sha512(seed))
        p = hash >> (hash.nbits() - bits)
        assert p.nbits() == bits
        return p.next_prime()


def generate_random_curves(attempts, bits, seed, cofactor_bound=8, cofactor_div=2, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curve = RandomEC(seed, bits, cofactor_bound=cofactor_bound, cofactor_div=cofactor_div)
    return generate_curves(attempts, count, curve)


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_random_curves(args.attempts, args.bits, args.seed, args.cofactor_bound, args.cofactor_div,
                                     args.count)
    results.to_json_file(args.outfile)
