"""
Curve25519 and Goldilocks according to https://datatracker.ietf.org/doc/html/rfc7748#appendix-A

Primes have been generated similarly as in  https://www.iacr.org/cryptodb/archive/2006/PKC/3351/3351.pdf (page 13), i.e. of the form 2^(32k-e)- where c is as small as possible and e \in {1,2,3}
"""

from dissectgen.standards.utils import embedding_degree, increment_seed, VerifiableCurve, generate_curves, \
    curve_command_line
from sage.all import ZZ, EllipticCurve, GF


class C25519(VerifiableCurve):
    def __init__(self, seed, p):
        if p % 4 == 1:
            conditions = {"p": p, "seed": seed, "cofactor_bound": 8, "cofactor_div": 2}
        else:
            conditions = {"p": p, "seed": seed, "cofactor_bound": 4, "cofactor_div": 2}
        super().__init__(conditions)
        self._standard = "c25519"
        self._category = "c25519"

    def set_ab(self):
        """Transformation from Montgomery to Weierstrass"""
        mont_a = ZZ(self._seed) * 4 + 2
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

        if cardinality % self._cofactor != 0 or not ZZ(cardinality / self._cofactor).is_prime():
            return
        order = cardinality // self._cofactor
        twist_card = 2 * (self._p + 1) - cardinality
        if twist_card % 4 != 0 or not ZZ(twist_card / 4).is_prime():
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

    def seed_update(self, offset=1):
        self._seed = increment_seed(self._seed, offset)
        self.clear()
        self.set_ab()

    def generate_generator(self):
        field = GF(self._p)
        u = field(0)
        point = 0, 0
        A = field(ZZ(self._seed) * 4 + 2)
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


def generate_c25519_curves(attempts, p, seed, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curve = C25519(seed, p)
    return generate_curves(attempts, count, curve)


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_c25519_curves(args.attempts, args.prime, args.seed, args.count)
    results.to_json_file(args.outfile)
