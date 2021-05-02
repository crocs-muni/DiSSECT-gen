"""This is an implementation of the SEC standard, see
    https://www.secg.org/sec2-v2.pdf
    https://www.secg.org/sec1-v2.pdf
"""
import os, json
from utils.utils import int_to_hex_string, embedding_degree_p, sha1, verifiably_random_curve, increment_seed
from sage.all import ZZ, floor, GF, Integer, EllipticCurve

STANDARD = 'secg'
PARAMETERS_FILE = os.path.join(STANDARD, f"parameters_{STANDARD}.json")


def large_prime_factor(m, bound):
    """
    Tests the size of the largest prime divisor of m
    """
    h, l = Integer(1), Integer(2)
    tmp = m
    while h < bound and l < bound:
        if tmp % l == 0:
            h *= l
            tmp = tmp // l
            continue
        l = l.next_prime()
    if h >= bound:
        return False
    if tmp.is_prime():
        return h
    return False


def verify_security(a, b, p, cofactor=0, embedding_degree_bound=100, verbose=False):
    cardinality = EllipticCurve(GF(p), [a, b]).__pari__().ellsea(cofactor)
    cardinality = Integer(cardinality)

    t = {192: 80, 512: 256}.get(p.nbits(), p.nbits() // 2)
    cofactor_bound = min(2 ** 20, 2 ** (t / 8))
    h = large_prime_factor(cardinality, cofactor_bound)
    if not h:
        return {}
    curve = {'cofactor': h, 'order': cardinality // h}
    if verbose:
        print("Checking MOV")
    if embedding_degree_p(p, curve['order']) < embedding_degree_bound:
        return {}
    if verbose:
        print("Checking Frob")
    if p == cardinality:
        return {}
    n_1_bound = floor(curve['order'] ** (1 - 19 / 20))
    if not (large_prime_factor(curve['order'] - 1, n_1_bound) and large_prime_factor(curve['order'] + 1, n_1_bound)):
        return {}
    curve['a'], curve['b'] = a, b
    return curve


def gen_point(seed, p, E, h):
    """Returns generator as specified in SEC"""
    A = bytearray("Base point", 'ASCII')
    B = bytearray.fromhex("01")
    S = bytearray.fromhex(seed)
    c = Integer(1)
    while True:
        C = bytearray.fromhex(int_to_hex_string(c))
        R = A
        for byte in [B, C, S]:
            R.extend(byte)
        e = ZZ(sha1(R).hexdigest(), 16)
        t = e % (2 * p)
        x, z = t % p, t // p
        c += 1
        try:
            y = E.lift_x(x)[1]
        except ValueError:
            continue
        if Integer(y) % 2 == z:
            return E(x, y) * h


def sec_curve(p, seed, cofactor):
    """Generates a SEC curve out of seed over Fp of any cofactor if cofactor!=1 otherwise cofactor=1"""
    return verifiably_random_curve(p, seed, cofactor, verify_security)


def generate_sec_curves(count, p, seed, cofactor_one=False):
    """This is an implementation of the SEC standard suitable for large-scale simulations
    For more readable implementation, see the secg.py
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

    with open(PARAMETERS_FILE, "r") as f:
        params = json.load(f)
        original_seed = params[str(bits)][1]

    for i in range(1, count + 1):
        current_seed = increment_seed(seed, -i)
        curve = sec_curve(current_seed, p, cofactor_one)
        if not curve:
            continue
        seed_diff = ZZ("0X" + original_seed) - ZZ("0X" + current_seed)
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
