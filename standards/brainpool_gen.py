"""This is an implementation of the Brainpool standard, see
    https://tools.ietf.org/pdf/rfc5639.pdf#15
    https://web.archive.org/web/20180417212206/http://www.ecc-brainpool.org/download/Domain-parameters.pdf
"""
import json
from sage.all import PolynomialRing, squarefree_part, BinaryQF, xsrange, gcd, ZZ, lcm, randint, \
    GF, EllipticCurve, Integer
from utils.utils import increment_seed, embedding_degree_p, find_integer, int_to_hex_string

CHECK_CLASS_NUMBER = False


def check_for_prime(n):
    """Checks whether n is suitable as a base field prime"""
    if n % 4 != 3:
        return False
    return n.is_prime()


def gen_prime(s, nbits):
    """Generates a nbits prime out of 160bit seed s"""
    while True:
        p = find_integer(s, nbits)
        while not check_for_prime(p):
            p += 1
        if 2 ** (nbits - 1) <= p <= 2 ** nbits - 1:
            return p
        s = increment_seed(s)


def find_a(field, s, nbits):
    """Out of 160bit seed s, finds coefficient a for y^2=x^3+ax+b over F_p where p has nbits"""
    z = PolynomialRing(field, 'z').gen()
    while True:
        a = find_integer(s, nbits, brainpool=True)
        if (a * z ** 4 + 3).roots():
            return a, s
        s = increment_seed(s)


def find_b(field, s, nbits):
    """Out of 160bit seed s, finds coefficient b for y^2=x^3+ax+b over F_p where p has nbits"""
    while True:
        b = find_integer(s, nbits, brainpool=True)
        if not field(b).is_square():
            return b, s
        s = increment_seed(s)


def check_discriminant(a, b, p):
    """Checks whether discriminant of y^2=x^3+ax+b over F_p is nonzero"""
    return (4 * a ** 3 + 27 * b ** 2) % p != 0


def class_number_check(curve, q, bound):
    """Tests whether the class number of curve is bounded by bound"""
    p = curve.base_field().order()
    t = p + 1 - q
    ndisc = t ** 2 - 4 * p
    disc = squarefree_part(-ndisc)
    if disc % 4 != 1:
        disc *= 4
    if disc % 4 == 0:
        neutral = BinaryQF([1, 0, -ndisc // 4])
    else:
        neutral = BinaryQF([1, 1, (1 - ndisc) // 4])
    class_lower_bound = 1

    def test_form_order(quad_form, order_bound, neutral_element):
        """Tests whether an order of quadratic form is smaller then bound"""
        tmp = quad_form
        for i in range(1, order_bound):
            if tmp.is_equivalent(neutral_element):
                return i
            tmp *= form
        return -1

    for a in xsrange(1, Integer(1 + ((-ndisc) // 3)).isqrt()):
        a4 = 4 * a
        s = ndisc + a * a4
        w = 1 + (s - 1).isqrt() if s > 0 else 0
        if w % 2 != ndisc % 2:
            w += 1
        for b in xsrange(w, a + 1, 2):
            t = b * b - ndisc
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


def security(curve, q):
    """Checks security conditions for curve"""
    p = curve.base_field().order()
    if q >= p:
        return False
    if p + 1 - q == 1:
        return False
    if not q.is_prime():
        return False
    if not (q - 1) / embedding_degree_p(p, q) < 100:
        return False
    if CHECK_CLASS_NUMBER and not class_number_check(curve, q, 10 ** 7):
        return False

    return True


def find_generator(scalar, field, curve):
    """Finds generator of curve as scalar*P where P has smallest x-coordinate"""
    a, b = curve.a4(), curve.a6()
    x = None
    for x in field:
        if (x ** 3 + a * x + b).is_square():
            break
    y = (x ** 3 + a * x + b).sqrt()
    y *= (-1) ** (randint(0, 1))
    point = curve(x, y)
    return scalar * point


def brainpool_curve(p, s, nbits):
    """Generates Brainpool curve over F_p (number of bits of p is nbits) out of 160bit seed"""
    field = GF(p)
    curve, q = None, None
    while True:
        a, s = find_a(field, s, nbits)
        s = increment_seed(s)
        b, s = find_b(field, s, nbits)
        if not check_discriminant(a, b, p):
            s = increment_seed(s)
            continue
        curve = EllipticCurve(field, [a, b])
        q = curve.__pari__().ellsea(1)
        if q == 0:
            s = increment_seed(s)
            continue
        q = Integer(q)
        if not security(curve, q):
            s = increment_seed(s)
            continue
        break
    s = increment_seed(s)
    k = find_integer(s, nbits, brainpool=True)
    return curve, find_generator(k, field, curve), q


def generate_brainpool_curves(count, p, seed):
    """This is an implementation of the Brainpool standard suitable for large-scale simulations
        For more readable implementation, see the brainpool.py
    """
    bits = p.nbits()
    sim_curves = {
        "name": "brainpool_sim_" + str(bits),
        "desc": "simulated curves generated according to the Brainpool standard",
        "initial_seed": seed,
        "seeds_tried": count,
        "curves": [],
        "seeds_successful": 0,
    }

    with open("standards/parameters/parameters_brainpool.json", "r") as f:
        params = json.load(f)
        original_seed = params[str(bits)][1]

    field = GF(p)
    z = PolynomialRing(field, 'z').gen()
    a = None
    for i in range(1, count + 1):
        if a is None:
            a = find_integer(seed, bits, brainpool=True)
            if not (a * z ** 4 + 3).roots():
                a = None
                seed = increment_seed(seed)
                continue
            seed = increment_seed(seed)
        b = find_integer(seed, bits, brainpool=True)
        if field(b).is_square():
            seed = increment_seed(seed)
            continue
        if not check_discriminant(a, b, p):
            seed = increment_seed(seed)
            a = None
            continue
        curve = EllipticCurve(field, [a, b])
        q = curve.__pari__().ellsea(1)
        if q == 0:
            seed = increment_seed(seed)
            a = None
            continue
        q = Integer(q)
        if not security(curve, q):
            seed = increment_seed(seed)
            a = None
            continue
        k = find_integer(increment_seed(seed), bits, brainpool=True)
        gen = find_generator(k, field, curve)
        x, y = Integer(gen[0]), Integer(gen[1])

        seed_diff = ZZ("0X" + seed) - ZZ("0X" + original_seed)
        sim_curve = {
            "name": "brainpool_sim_" + str(bits) + "_seed_diff_" + str(seed_diff),
            "category": sim_curves["name"],
            "desc": "",
            "field": {
                "type": "Prime",
                "p": int_to_hex_string(p),
                "bits": bits,
            },
            "form": "Weierstrass",
            "params": {"a": {"raw": int_to_hex_string(a)},
                       "b": {"raw": int_to_hex_string(b)}},
            "generator": {"x": {"raw": int_to_hex_string(x)},
                          "y": {"raw": int_to_hex_string(y)}},
            "order": q,
            "cofactor": 1,
            "characteristics": None,
            "seed": seed,
            "seed_diff": seed_diff,
        }
        sim_curves["curves"].append(sim_curve)
        sim_curves["seeds_successful"] += 1
        seed = increment_seed(seed)

    return sim_curves
