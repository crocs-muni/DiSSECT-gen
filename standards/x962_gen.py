import json, os
from random import randint
from utils.utils import increment_seed, int_to_hex_string, embedding_degree_p, verifiably_random_curve
from sage.all import Integers, ZZ, GF, EllipticCurve, prime_range, is_pseudoprime, sqrt

STANDARD = 'x962'
PARAMETERS_FILE = os.path.join('standards','parameters', f"parameters_{STANDARD}.json")


def verify_near_primality(u, r_min, l_max=255):
    """Verifying near primarility according to the standard"""
    n = u
    h = 1
    for l in prime_range(l_max):
        while n % l == 0:
            n = ZZ(n / l)
            h = h * l
            if n < r_min:
                return {}
    if is_pseudoprime(n):
        return {'cofactor': h, 'order': n}
    return {}


def verify_security(a, b, p, cofactor=0, embedding_degree_bound=20, verbose=False):
    """Checks the security according to the standard"""
    cardinality = EllipticCurve(GF(p), [a, b]).__pari__().ellsea(cofactor)
    cardinality = ZZ(cardinality)
    # a somewhat arbitrary bound (more strict than in the standard), but it will speed up the generation process
    r_min_bits = cardinality.nbits() - 5
    r_min = max(2 ** r_min_bits, 4 * sqrt(p))
    if verbose:
        print("Checking near-primality of", cardinality)
    curve = verify_near_primality(cardinality, r_min)
    if not curve:
        return {}
    if verbose:
        print("Checking MOV")
    if embedding_degree_p(p, curve['order']) < embedding_degree_bound:
        return {}
    if verbose:
        print("Checking Frob")
    if p == cardinality:
        return {}
    curve['a'], curve['b'] = a, b
    return curve


def x962_curve(p, seed, cofactor):
    """Generates a x962 curve out of seed over Fp of any cofactor if cofactor!=1 otherwise cofactor=1"""
    return verifiably_random_curve(p, seed, cofactor, verify_security)


def random_point(a, b, p):
    """Generates a random point according to the standard. Currently not used."""

    while True:
        x = randint(0, p)
        L = (x ** 3 + a * x + b) % p
        if L == 0:
            return x, 0
        if not L.is_square():
            continue
        return x, ZZ(Integers(p)(L).sqrt())


def generate_point(a, b, h, p):
    """Generates a generator for a curve according to the standards. Currently not used."""
    E = EllipticCurve(GF(p), [a, b])
    while True:
        R = E(*random_point(a, b, p))
        G = h * R
        if G == E(0):
            continue
        return G


def generate_x962_curves(count, p, seed, cofactor_one=False, std_seed='00'):
    """Generates at most #count curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    bits = p.nbits()
    sim_curves = {
        "name": f"{STANDARD}_sim_{str(bits)}",
        "desc": f"simulated curves generated according to the {STANDARD} standard",
        "initial_seed": seed,
        "seeds_tried": count,
        "curves": [],
        "seeds_successful": 0,
    }

    for i in range(1, count + 1):
        current_seed = increment_seed(seed, -i)
        curve = x962_curve(current_seed, p, cofactor_one)
        if not curve:
            continue
        seed_diff = ZZ("0X" + std_seed) - ZZ("0X" + current_seed)
        sim_curve = {
            "name": f"{STANDARD}_sim_{str(bits)}_seed_diff_{str(seed_diff)}",
            "category": sim_curves["name"],
            "desc": "",
            "field": {
                "type": "Prime",
                "p": int_to_hex_string(p),
                "bits": bits,
            },
            "form": "Weierstrass",
            "params": {"a": {"raw": int_to_hex_string(curve['a'])}, "b": {"raw": int_to_hex_string(curve['b'])}},
            "generator": {"x": {"raw": ""}, "y": {"raw": ""}},
            "order": curve['order'],
            "cofactor": curve['cofactor'],
            "characteristics": None,
            "seed": current_seed,
            "seed_diff": seed_diff,
        }
        sim_curves["curves"].append(sim_curve)
        sim_curves["seeds_successful"] += 1

    return sim_curves
