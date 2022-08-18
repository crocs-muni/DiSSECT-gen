"""Some useful functions for the project"""
import copy

from sage.all import Integers, ceil, floor, GF, EllipticCurve
from abc import ABC, abstractmethod
from sage.all import squarefree_part, BinaryQF, xsrange, gcd, ZZ, lcm, Integer
import hashlib
import json, argparse

STANDARDS = ['x962', 'brainpool', 'secg', 'nums', 'nist', 'bls', 'random', 'c25519', 'bn']


def increment_seed(seed: str, i=1) -> str:
    """Increments hex-string seed (without prefix) by i (can be negative)"""
    g = len(seed) * 4 - 8
    g = g % 8 + g
    f = "0" + str(len(seed) - 2) + "x"
    return '0x' + format(ZZ(Integers(2 ** g)(ZZ(seed) + i)), f)


def next_hamming(val):
    c = val & -val
    r = val + c
    return ZZ((((r ^ val) >> 2) // c) | r)


def seed_update(std, seed, offset):
    return increment_seed(seed, offset)


def sha1(x: str) -> str:
    """Returns sha1 value of hex-string x in hex-string"""
    return '0x' + hashlib.sha1(bytes.fromhex((len(x) % 2) * "0" + x[2:])).hexdigest()


def sha512(x: str) -> str:
    """Returns sha512 value of hex-string x in hex-string"""
    return '0x' + hashlib.sha3_512(bytes.fromhex((len(x) % 2) * "0" + x[2:])).hexdigest()


def int_to_hex_string(x: ZZ, prefix=True) -> str:
    """Converts int to hex string (without prefix)"""
    f = "0" + str(ceil(x.nbits() / 8) * 2) + "x"
    return prefix * "0x" + format(x, f)


def embedding_degree(prime: ZZ, order: int) -> int:
    """Returns embedding degree with respect to p"""
    return Integers(order)(prime).multiplicative_order()


def rightmost_bits(h: str, nbits: int) -> str:
    """Returns nbits of rightmost bits of hex-string h"""
    return int_to_hex_string(ZZ(h) & ((1 << nbits) - 1))


def find_integer(seed: str, nbits: int, brainpool_prime=False) -> ZZ:
    """Generates integer in [0,2^nbits - 1] from a seed s of 160-bit length
    modified = True corresponds to find_integer2 as defined by Brainpool"""
    seed = "0x" + "0" * (42 - len(seed)) + seed[2:]
    v = floor((nbits - 1) / 160)
    w = nbits - 160 * v - (1 - brainpool_prime)
    h = bytes.fromhex(rightmost_bits(sha1(seed), w)[2:])
    for i in range(1, v + 1):
        s_i = rightmost_bits(increment_seed(seed, i), 160)
        h += hashlib.sha1(bytes.fromhex(s_i[2:])).digest()
    return ZZ(h.hex(), 16)


def get_b_from_r(r: ZZ, prime: ZZ, a=ZZ(-3)):
    """Gets a parameter b of elliptic curve out of a random value r"""
    a = GF(prime)(a)
    if (a ** 3 / r).is_square():
        return ZZ((a ** 3 / r).sqrt())
    return None


class VerifiableCurve(ABC):
    """
    Abstract class for a representation of curves and their generation (method find_curve).
    Expected work-flow: Initial input is a seed, prime for the base-field, cofactor bounds.
    Curves are generated using find_curve based on some initial value of parameter (seed), see the method.
    This parameter is updated using seed_update. For each such value a curve is defined using set_ab and its security
    is checked using security method. Regarding the CM-method procedures, the security method will be used before
    the set_ab method.


    Methods set_ab,seed_update, security must be implemented.

    :param conditions: A dictionary with conditions on the curve. Supported options:
        'seed': any initial value that will be updated to generate curves (can be None)
        'p': prime defining the base-field of the curve (can be None)
        'cofactor_bound': an upper bound on the cofactor (can be None)
        'cofactor_div': a product of primes that are permitted to occur in the factorization of the cofactor (can be None)
        'set_ab': True(default)/False require to define curve parameters
    """

    def __init__(self, conditions):
        self._a = None
        self._b = None
        self._p = None
        self._cardinality = None
        self._order = None
        self._standard = None
        self._cofactor = None
        self._generator = None
        self._category = None
        self._embedding_degree = None
        self._cm = None
        self._j_invariant = None
        self._secure = None
        self._curve = None
        self._cofactor_div = None
        self._cofactor_bound = None
        self._cm_method = False

        if 'seed' in conditions:
            self._seed = conditions['seed']

        if 'p' in conditions:
            self._p = conditions['p']
            self._bits = self._p.nbits()
            self._field = GF(self._p)

        if 'cofactor_div' in conditions:
            self._cofactor_div = conditions['cofactor_div']
        if 'cofactor_bound' in conditions:
            self._cofactor_bound = ZZ(conditions['cofactor_bound'])

        if 'set_ab' not in conditions or conditions['set_ab']:
            self.set_ab()

        if "cm_method" in conditions and conditions["cm_method"]:
            self._cm_method = True

    def a(self):
        return self._a

    def b(self):
        return self._b

    def cofactor(self):
        return self._cofactor

    def seed(self):
        return self._seed

    def order(self):
        return self._order

    def category(self):
        return self._category

    def bits(self):
        return self._bits

    @abstractmethod
    def set_ab(self):
        """
        Method for defining curve parameters (e.g., from seed).
        """
        pass

    @abstractmethod
    def seed_update(self, offset=1):
        """
        Method used for updating the seed during curve generation (see find_curve).
        """
        pass

    @abstractmethod
    def security(self):
        """
        Method for checking security (and possibly other conditions) of the curve
        Sets the attribute _secure to True or False
        """
        pass

    def generate_generator(self):
        """
        Optional method for generating group generator.
        Sets the attribute _generator
        """
        pass

    def find_curve(self):
        if self.not_defined() and not self._cm_method:
            self.set_ab()
        while not self.secure():
            self.seed_update()
        self.generate_generator()
        self.compute_properties()

    def not_defined(self):
        return self._a is None or self._b is None

    def clear(self):
        self._a = None
        self._b = None
        self._secure = None
        self._curve = None

    def curve(self):
        if self._curve is None:
            self._curve = EllipticCurve(GF(self._p), [self._a, self._b])
        return self._curve

    def secure(self):
        if self._secure is None:
            self.security()
        return self._secure

    def trace(self):
        return self._p + 1 - self._cardinality

    def compute_properties(self):
        if self._j_invariant is None:
            self._j_invariant = self.curve().j_invariant()
        if self._embedding_degree is None:
            self._embedding_degree = embedding_degree(self._p, self._order)
        if self._cm is None:
            d = self.trace() ** 2 - 4 * self._p
            d = d.squarefree_part()
            self._cm = 4 * d if d % 4 != 1 else d

    def properties(self):
        self.compute_properties()
        return {"cm_discriminant": hex(self._cm), "embedding_degree": hex(self._embedding_degree),
                "trace": hex(self.trace()), "j_invariant": hex(self._j_invariant)}

    def generator(self):
        if self._generator is None:
            return "", ""
        return list(map(lambda x: int_to_hex_string(ZZ(x)), self._generator[:2]))

    def json_export(self):
        return {"name": f"{self._standard}_sim_{str(self._bits)}_{self._seed}", "category": f"{self._category}_sim",
                "desc": "",
                "field": {"type": "Prime", "p": int_to_hex_string(self._p, prefix=True), "bits": self._bits},
                "form": "Weierstrass", "params": {"a": {"raw": int_to_hex_string(ZZ(self._a), prefix=True)},
                                                  "b": {"raw": int_to_hex_string(ZZ(self._b), prefix=True)}},
                "generator": {"x": {"raw": self.generator()[0]}, "y": {"raw": self.generator()[1]}},
                "order": self._order,
                "cofactor": self._cofactor, "properties": self.properties(), "seed": self._seed}


class SimulatedCurves:
    def __init__(self, standard, bits, initial_seed, attempts):
        self._curves = []
        self._bits = bits
        self._attempts = attempts
        self._initial_seed = initial_seed
        self._standard = standard

    def curves(self):
        return self._curves

    def json_export(self):
        """Prepares a list of dictionaries representing curves for json file"""
        return {"name": f"{self._standard}_sim_" + str(self._bits),
                "desc": f"simulated curves generated according to the {self._standard} standard",
                "initial_seed": self._initial_seed,
                "seeds_tried": self._attempts, "seeds_successful": len(self._curves),
                "curves": [curve.json_export() for curve in self._curves]}

    def add_curve(self, curve: VerifiableCurve):
        self._curves.append(curve)

    def to_json_file(self, filename):
        with open(filename, "w+") as f:
            json.dump(self.json_export(), f, indent=2, cls=IntegerEncoder)


def generate_curves(attempts, count, curve):
    """This is an implementation of the SEC standard suitable for large-scale simulations
    """
    simulated_curves = SimulatedCurves(curve.category(), curve.bits(), curve.seed(), attempts)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if not curve.secure():
            curve.seed_update()
            continue
        curve.generate_generator()
        curve.compute_properties()
        simulated_curves.add_curve(copy.deepcopy(curve))
        c += 1
        curve.seed_update()
    return simulated_curves


def seed_order(files, standard):
    """Sorts through files with results according to the right ordering of seeds"""
    if standard == 'bls':
        def bls_sort(x):
            x = int((x.split(".")[-2]).split("_")[-1], 16)
            return bin(x).count("1"), -x

        return sorted(files, key=lambda x: bls_sort(x))
    return sorted(files, key=lambda x: abs(int((x.split(".")[-2]).split("_")[-1], 16)))


def class_number_check(curve: EllipticCurve, q: ZZ, bound: int):
    """Tests whether the class number of curve is lower-bounded by bound"""
    p = curve.base_field().order()
    t = p + 1 - q
    whole_disc = t ** 2 - 4 * p
    disc = squarefree_part(-whole_disc)
    if disc % 4 != 1:
        disc *= 4
    if disc % 4 == 0:
        neutral = BinaryQF([1, 0, -whole_disc // 4])
    else:
        neutral = BinaryQF([1, 1, (1 - whole_disc) // 4])
    class_lower_bound = 1

    def test_form_order(quad_form, order_bound, neutral_element):
        """Tests whether an order of quadratic form is smaller then bound"""
        tmp = quad_form
        for i in range(1, order_bound):
            if tmp.is_equivalent(neutral_element):
                return i
            tmp *= form
        return -1

    for a in xsrange(1, ZZ(1 + ((-whole_disc) // 3)).isqrt()):
        a4 = 4 * a
        s = whole_disc + a * a4
        w = 1 + (s - 1).isqrt() if s > 0 else 0
        if w % 2 != whole_disc % 2:
            w += 1
        for b in xsrange(w, a + 1, 2):
            t = b * b - whole_disc
            if t % a4 == 0:
                c = t // a4
                if gcd([a, b, c]) == 1:
                    if 0 < b < a < c:
                        form = BinaryQF([a, -b, c])
                    else:
                        form = BinaryQF([a, b, c])
                    order = test_form_order(form, bound, neutral)
                    if order == -1:
                        return True
                    class_lower_bound = lcm(class_lower_bound, order)
                    if class_lower_bound > bound:
                        return True
    return False


"""Handler for json imports and dumps"""
FLOAT_PRECISION = 5


class IntegerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Integer):
            return int(obj)
        if isinstance(obj, float):
            return round(obj, 5)
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


def curve_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=ZZ)
    parser.add_argument("--prime", type=ZZ)
    parser.add_argument("--seed")
    parser.add_argument("--cofactor_bound")
    parser.add_argument("--cofactor_div", type=ZZ)
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--outfile")
    return parser.parse_args()
