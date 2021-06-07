from utils.utils import increment_seed, embedding_degree, verifiably_random_curve, curves_json_wrap, sha1
from sage.all import ZZ, GF, EllipticCurve
import x962_gen as x962
import secg_gen as secg


def verify_security(a: ZZ, b: ZZ, prime: ZZ, cofactor=0, embedding_degree_bound=100, verbose=False) -> dict:
    """Checks the security according to the standard"""
    cardinality = EllipticCurve(GF(prime), [a, b]).__pari__().ellsea(cofactor)
    cardinality = ZZ(cardinality)
    if cardinality == 0:
        return {}
    r_min = max(2 ** (prime.nbits() - 1), 2 ** 160)
    if verbose:
        print("Checking near-primality of", cardinality)
    curve = x962.verify_near_primality(cardinality, r_min)
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


def nist_curve(seed, p, cofactor):
    """Generates a nist curve out of seed over Fp of any cofactor if cofactor!=1 otherwise cofactor=1"""
    return verifiably_random_curve(seed, p, cofactor, verify_security)


def generate_point(seed: str, p: ZZ, curve: EllipticCurve, h: ZZ):
    """Returns generator, currently not using"""
    return secg.gen_point(seed, p, curve, h)


def generate_nist_curves(count, p, seed, cofactor_one=False):
    """Generates at most #count curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curves = []
    for i in range(1, count + 1):
        current_seed = increment_seed(seed, -i)
        curve = nist_curve(current_seed, p, cofactor_one)
        if curve:
            curve['generator'] = (ZZ(0), ZZ(0))
            curve['seed'] = current_seed
            curve['prime'] = p
            curves.append(curve)
    return curves_json_wrap(curves, p, count, seed, 'nist')
