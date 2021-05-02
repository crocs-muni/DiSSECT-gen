from sage.all import Integers, ZZ, ceil, floor, GF
import hashlib


# ============================================================
def increment_seed(seed, i=1):
    """accepts a hex string as input (not starting with 0x)"""
    g = ZZ(seed, 16).nbits()
    f = "0" + str(len(seed)) + "X"
    return format(ZZ(Integers(2 ** g)(ZZ(seed, 16) + i)), f)


def sha1(x):
    """Returns sha1 of x in hex"""
    return hashlib.sha1(bytes.fromhex(x)).hexdigest()


def int_to_hex_string(x):
    """Converts int to hex string"""
    f = "0" + str(ceil(x.nbits() / 8) * 2) + "X"
    return format(ZZ(x, 16), f)


def embedding_degree_p(p, r):
    """returns embedding degree with respect to p"""
    return Integers(r)(p).multiplicative_order()


def rightmost_bits(h, nbits):
    """Returns nbits of rightmost bits of h"""
    return int_to_hex_string(ZZ(h, 16) % (2 ** nbits))


def concatenate_bytearrays(bytearrays):
    """Concatenates list of bytearrays"""
    r = bytearray.fromhex(bytearrays[0])
    for h in bytearrays[1:]:
        r.extend(bytearray.fromhex(h))
    return r.hex()


# ============================================================


def find_integer(s, nbits, brainpool=False):
    """Generates integer in [0,2^nbits - 1] from a seed s of 160-bit length
    modified = True corresponds to find_integer2 as defined by brainpool"""
    v = floor((nbits - 1) / 160)
    w = nbits - 160 * v - brainpool
    h = sha1(s)
    z = ZZ(s, 16)
    bytearrays = [rightmost_bits(h, w)]
    for i in range(1, v + 1):
        z_i = (z + i) % (2 ** 160)
        s_i = int_to_hex_string(z_i)
        bytearrays.append(sha1(s_i))
    h = concatenate_bytearrays(bytearrays)
    return ZZ(h, 16)


def get_b_from_r(r, p, a=ZZ(-3)):
    """Gets the parameter b out of the random value r"""
    F = GF(p)
    if F(a ** 3 / r).is_square():
        return ZZ(F(a ** 3 / r).sqrt())
    else:
        return None


def verifiably_random_curve(seed, p, cofactor, security_function):
    r = find_integer(seed, p.nbits())
    b = get_b_from_r(r, p)
    a = ZZ(-3)
    if b is None or (4 * a ** 3 + 27 * b ** 2) % p == 0:
        return {}
    curve = security_function(a, b, p, cofactor)
    if curve:
        return curve
    if p % 4 == 3:
        curve = security_function(a, p - b, p, cofactor)
    return curve
