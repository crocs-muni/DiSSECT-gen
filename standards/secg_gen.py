""" Implementation of the SEC standard, see
    https://www.secg.org/sec2-v2.pdf
    https://www.secg.org/sec1-v2.pdf
"""

from utils.utils import embedding_degree, sha1, verifiably_random_curve, increment_seed, curves_json_wrap
from sage.all import ZZ, floor, GF, Integer, EllipticCurve


def large_prime_factor(m: ZZ, bound: int):
    """Tests if the size of the largest prime divisor of m is upper-bounded by bound"""
    h, prime = Integer(1), Integer(2)
    tmp = m
    while h < bound and prime < bound:
        if tmp % prime == 0:
            h *= prime
            tmp = tmp // prime
            continue
        prime = prime.next_prime()
    if h >= bound:
        return False
    if tmp.is_prime():
        return h
    return False


def verify_security(a: ZZ, b: ZZ, prime: ZZ, cofactor=2, embedding_degree_bound=100, verbose=False) -> dict:
    try:
        cardinality = EllipticCurve(GF(prime), [a, b]).__pari__().ellsea(cofactor)
    except ArithmeticError:
        return {}
    cardinality = Integer(cardinality)
    if cardinality == 0:
        return {}
    #t = {192: 80, 512: 256}.get(prime.nbits(), prime.nbits() // 2)
    cofactor_bound = 4#2 ** (t / 8)
    h = large_prime_factor(cardinality, cofactor_bound)
    if not h:
        return {}
    curve = {'cofactor': h, 'order': cardinality // h}
    if verbose:
        print("Checking MOV")
    if embedding_degree(prime, curve['order']) < embedding_degree_bound:
        return {}
    if verbose:
        print("Checking if curve is anomalous")
    if prime == cardinality:
        return {}
    n_1_bound = floor(curve['order'] ** (1 - 19 / 20))
    if not (large_prime_factor(curve['order'] - 1, n_1_bound) and large_prime_factor(curve['order'] + 1, n_1_bound)):
        return {}
    curve['a'], curve['b'] = a, b
    return curve


def gen_point(seed: str, p: ZZ, curve: EllipticCurve, h: ZZ):
    """Returns generator as specified in SEC, currently not using"""
    c = 1
    while True:
        r = bytes("Base point", 'ASCII') + bytes([1]) + bytes([c]) + bytes.fromhex(seed)
        e = ZZ(sha1(r.hex()), 16)
        t = e % (2 * p)
        x, z = t % p, t // p
        c += 1
        try:
            y = curve.lift_x(x)[1]
        except ValueError:
            continue
        if Integer(y) % 2 == z:
            return curve(x, y) * h


def sec_curve(seed,p, cofactor):
    """Generates a SEC curve out of seed over Fp of any cofactor if cofactor!=1 otherwise cofactor=1"""
    return verifiably_random_curve(seed,p, cofactor, verify_security)


def generate_sec_curves(count, p, seed, cofactor_one=2):
    """This is an implementation of the SEC standard suitable for large-scale simulations
    """
    curves = []
    for i in range(1, count + 1):
        current_seed = increment_seed(seed, -i)
        curve = sec_curve(current_seed, p, cofactor_one)
        if curve:
            curve['generator'] = (ZZ(0), ZZ(0))
            curve['seed'] = current_seed
            curve['prime'] = p
            curves.append(curve)
    return curves_json_wrap(curves, p, count, seed, 'secg')
