from random import randint
from utils.utils import increment_seed, embedding_degree, verifiably_random_curve, curves_json_wrap
from sage.all import Integers, ZZ, GF, EllipticCurve, prime_range, is_pseudoprime, sqrt


def verify_near_primality(u: ZZ, r_min: ZZ, l_max=255) -> dict:
    """Verifying near primality according to the standard"""
    n = u
    h = 1
    for prime in prime_range(l_max):
        while n % prime == 0:
            n = ZZ(n / prime)
            h = h * prime
            if n < r_min:
                return {}
    if is_pseudoprime(n):
        return {'cofactor': h, 'order': n}
    return {}


def verify_security(a: ZZ, b: ZZ, prime: ZZ, cofactor=0, embedding_degree_bound=20, verbose=False) -> dict:
    """Checks the security according to the standard"""
    cardinality = EllipticCurve(GF(prime), [a, b]).__pari__().ellsea(cofactor)
    cardinality = ZZ(cardinality)
    # a somewhat arbitrary bound (more strict than in the standard), but it will speed up the generation process
    r_min_bits = cardinality.nbits() - 5
    r_min = max(2 ** r_min_bits, 4 * sqrt(prime))
    if verbose:
        print("Checking near-primality of", cardinality)
    curve = verify_near_primality(cardinality, r_min)
    if not curve:
        return {}
    if verbose:
        print("Checking MOV")
    if embedding_degree(prime, curve['order']) < embedding_degree_bound:
        return {}
    if verbose:
        print("Checking if curve is anomalous")
    if prime == cardinality:
        return {}
    curve['a'], curve['b'] = a, b
    return curve


def x962_curve(seed, p, cofactor):
    """Generates a x962 curve out of seed over Fp of any cofactor if cofactor!=1 otherwise cofactor=1"""
    return verifiably_random_curve(seed,p, cofactor, verify_security)


def random_point(a, b, p):
    """Generates a random point according to the standard. Currently not used."""
    while True:
        x = randint(0, p)
        y2 = (x ** 3 + a * x + b) % p
        if y2 == 0:
            return x, 0
        if not y2.is_square():
            continue
        return x, ZZ(Integers(p)(y2).sqrt())


def generate_point(a, b, h, p):
    """Generates a generator for a curve according to the standards. Currently not used."""
    curve = EllipticCurve(GF(p), [a, b])
    while True:
        r = curve(*random_point(a, b, p))
        g = h * r
        if g == curve(0):
            continue
        return g


def generate_x962_curves(count, p, seed, cofactor_one=False):
    """Generates at most #count curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curves = []
    for i in range(1, count + 1):
        current_seed = increment_seed(seed, -i)
        curve = x962_curve(current_seed, p, cofactor_one)
        if curve:
            curve['generator'] = (ZZ(0), ZZ(0))
            curve['seed'] = current_seed
            curve['prime'] = p
            curves.append(curve)
    return curves_json_wrap(curves, p, count, seed, 'x962')
