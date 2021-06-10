"""Implementation of the Brainpool standard, see
    https://tools.ietf.org/pdf/rfc5639.pdf#15
"""
from sage.all import PolynomialRing, squarefree_part, BinaryQF, xsrange, gcd, ZZ, lcm, randint, GF, EllipticCurve
from utils.utils import increment_seed, embedding_degree, find_integer, curves_json_wrap

CHECK_CLASS_NUMBER = False


def check_for_prime(n: ZZ):
    """Checks whether n is suitable as a base field prime"""
    if n % 4 != 3:
        return False
    return n.is_prime()


def gen_prime(seed: str, nbits: int) -> ZZ:
    """Generates a prime of length nbits out of 160bit seed s"""
    while True:
        p = find_integer(seed, nbits, brainpool_prime=True)
        while not check_for_prime(p):
            p += 1
        if p.nbits() == nbits:
            return p
        seed = increment_seed(seed)


def find_a(field: GF, seed: str, nbits: int) -> ZZ:
    """Out of 160bit seed s, finds coefficient a for y^2=x^3+ax+b over F_p where p has nbits"""
    z = PolynomialRing(field, 'z').gen()
    while True:
        a = find_integer(seed, nbits)
        if (a * z ** 4 + 3).roots():
            return a, seed
        seed = increment_seed(seed)


def find_b(field: GF, seed: str, nbits: int) -> (ZZ, str):
    """Out of 160bit seed s, finds coefficient b for y^2=x^3+ax+b over F_p where p has nbits"""
    while True:
        b = find_integer(seed, nbits)
        if not field(b).is_square():
            return b, seed
        seed = increment_seed(seed)


def check_discriminant(a, b, p):
    """Checks whether discriminant of y^2=x^3+ax+b over F_p is nonzero"""
    return (4 * a ** 3 + 27 * b ** 2) % p != 0


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


def security(curve: EllipticCurve, order: ZZ):
    """Checks security conditions for curve"""
    p = curve.base_field().order()
    if order >= p:
        return False
    if not order.is_prime():
        return False
    if not (order - 1) / embedding_degree(prime=p, order=order) < 100:
        return False
    if CHECK_CLASS_NUMBER and not class_number_check(curve, order, 10 ** 7):
        return False
    return True


def find_generator(scalar: ZZ, curve: EllipticCurve):
    """Finds generator of curve as scalar*P where P has smallest x-coordinate"""
    a, b = curve.a4(), curve.a6()
    x = None
    for x in curve.base_field():
        if (x ** 3 + a * x + b).is_square():
            break
    y = (x ** 3 + a * x + b).sqrt()
    y *= (-1) ** (randint(0, 1))
    point = curve(x, y)
    return scalar * point


def brainpool_curve(prime: ZZ, seed: str, nbits: int) -> dict:
    """Generates Brainpool curve over F_p (number of bits of p is nbits) out of 160bit seed"""
    field = GF(prime)
    curve, order = None, None
    while True:
        a, seed = find_a(field, seed, nbits)
        seed = increment_seed(seed)
        b, seed = find_b(field, seed, nbits)
        if not check_discriminant(a, b, prime):
            seed = increment_seed(seed)
            continue
        try:
            curve = EllipticCurve(field, [a, b])
        except ArithmeticError:
            seed = increment_seed(seed)
            continue
        order = curve.__pari__().ellsea(1)
        if order == 0:
            seed = increment_seed(seed)
            continue
        order = ZZ(order)
        if not security(curve, order):
            seed = increment_seed(seed)
            continue
        break
    seed = increment_seed(seed)
    k = find_integer(seed, nbits)
    generator = find_generator(k, curve)
    return {'a': a, 'b': b, 'generator': (ZZ(generator[0]), ZZ(generator[1])), 'order': order}


def generate_brainpool_curves(count: int, p: ZZ, initial_seed: str) -> dict:
    """This is an implementation of the Brainpool standard suitable for large-scale simulations
        For more readable implementation, see 'brainpool_curve' above
    """
    curves = []
    bits = p.nbits()
    field = GF(p)
    z = PolynomialRing(field, 'z').gen()
    a = None
    seed = initial_seed
    correct_seed = None
    for i in range(1, count + 1):
        if a is None:
            a = find_integer(seed, bits)
            if not (a * z ** 4 + 3).roots():
                a = None
                seed = increment_seed(seed)
                continue
            correct_seed = seed
            seed = increment_seed(seed)
        b = find_integer(seed, bits)
        if field(b).is_square():
            seed = increment_seed(seed)
            continue
        if not check_discriminant(a, b, p):
            seed = increment_seed(seed)
            a = None
            continue
        try:
            curve = EllipticCurve(field, [a, b])
        except ArithmeticError:
            a = None
            seed = increment_seed(seed)
            continue
        order = curve.__pari__().ellsea(1)
        if order == 0:
            seed = increment_seed(seed)
            a = None
            continue
        order = ZZ(order)
        if not security(curve, order):
            seed = increment_seed(seed)
            a = None
            continue
        k = find_integer(increment_seed(seed), bits)
        gen = find_generator(k, curve)
        curves.append(
            {'a': ZZ(a), 'b': ZZ(b), 'order': order, 'cofactor': 1, 'seed': correct_seed, 'prime': p,
             'generator': (ZZ(gen[0]), ZZ(gen[1]))})
        seed = increment_seed(seed)

    return curves_json_wrap(curves, p, count, initial_seed, standard='brainpool')
