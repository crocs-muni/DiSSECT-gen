"""Some useful functions for the project"""

from sage.all import Integers, ZZ, ceil, floor, GF
import hashlib

STANDARDS = ['x962', 'brainpool', 'secg','nums','nist']


def increment_seed(seed: str, i=1) -> str:
    """Increments hex-string seed (without prefix) by i (can be negative)"""
    g = ZZ(seed, 16).nbits()
    f = "0" + str(len(seed)) + "X"
    return format(ZZ(Integers(2 ** g)(ZZ(seed, 16) + i)), f)


def sha1(x: str) -> str:
    """Returns sha1 value of hex-string x (without prefix) in hex-string"""
    return hashlib.sha1(bytes.fromhex(x)).hexdigest()


def int_to_hex_string(x: ZZ) -> str:
    """Converts int to hex string (without prefix)"""
    f = "0" + str(ceil(x.nbits() / 8) * 2) + "X"
    return format(ZZ(x, 16), f)


def embedding_degree(prime: ZZ, order: int) -> int:
    """Returns embedding degree with respect to p"""
    return Integers(order)(prime).multiplicative_order()


def rightmost_bits(h: str, nbits: int) -> str:
    """Returns nbits of rightmost bits of hex-string h"""
    return int_to_hex_string(ZZ(h, 16) & ((1 << nbits) - 1))


def find_integer(seed: str, nbits: int, brainpool_prime=False) -> ZZ:
    """Generates integer in [0,2^nbits - 1] from a seed s of 160-bit length
    modified = True corresponds to find_integer2 as defined by Brainpool"""
    v = floor((nbits - 1) / 160)
    w = nbits - 160 * v - (1 - brainpool_prime)
    h = bytes.fromhex(rightmost_bits(sha1(seed), w))
    for i in range(1, v + 1):
        s_i = rightmost_bits(increment_seed(seed, i), 160)
        h += hashlib.sha1(bytes.fromhex(s_i)).digest()
    return ZZ(h.hex(), 16)


def get_b_from_r(r: ZZ, prime: ZZ, a=ZZ(-3)):
    """Gets a parameter b of elliptic curve out of a random value r"""
    a = GF(prime)(a)
    if (a ** 3 / r).is_square():
        return ZZ((a ** 3 / r).sqrt())
    return None


def verifiably_random_curve(seed: str, prime: ZZ, cofactor: int, security_function) -> dict:
    """Generates verifiably random curve (dictionary)"""
    r = find_integer(seed, prime.nbits())
    b = get_b_from_r(r, prime)
    a = ZZ(-3)
    if b is None or (4 * a ** 3 + 27 * b ** 2) % prime == 0:
        return {}
    curve = security_function(a=a, b=b, prime=prime, cofactor=cofactor)
    if curve:
        return curve
    if prime % 4 == 3:
        curve = security_function(a=a, b=prime - b, prime=prime, cofactor=cofactor)
    return curve


def curves_json_wrap(curves: list, p: ZZ, tries: int, seed: str, standard: str) -> dict:
    """Prepares a list of dictionaries representing curves for json file"""
    sim_curves = {
        "name": f"{standard}_sim_" + str(p.nbits()),
        "desc": f"simulated curves generated according to the {standard} standard",
        "initial_seed": seed,
        "seeds_tried": tries,
        "curves": [],
        "seeds_successful": len(curves),
    }
    for curve in curves:
        sim_curve = {
            "name": f"{standard}_sim_" + str(p.nbits()) + "_" + curve['seed'],
            "category": sim_curves["name"],
            "desc": "",
            "field": {
                "type": "Prime",
                "p": int_to_hex_string(p),
                "bits": p.nbits(),
            },
            "form": "Weierstrass",
            "params": {"a": {"raw": int_to_hex_string(curve['a'])},
                       "b": {"raw": int_to_hex_string(curve['b'])}},
            "generator": {"x": {"raw": int_to_hex_string(curve['generator'][0])},
                          "y": {"raw": int_to_hex_string(curve['generator'][1])}},
            "order": curve['order'],
            "cofactor": curve['cofactor'],
            "characteristics": None,
            "seed": curve['seed']
        }
        sim_curves["curves"].append(sim_curve)
    return sim_curves


def seed_update(seed, offset, standard):
    """Defines incrementing/decrementing for large-scale generation of curves
    x962 generation is decrementing from std seed
    """
    if standard == 'x962':
        return increment_seed(seed, -offset)
    return increment_seed(seed, offset)


def seed_order(files, standard):
    """Sorts through files with results according to the right ordering of seeds"""
    if standard == 'x962':
        return sorted(files, key=lambda x: int((x.split(".")[-2]).split("_")[-1], 16), reverse=True)
    return sorted(files, key=lambda x: int((x.split(".")[-2]).split("_")[-1], 16))
