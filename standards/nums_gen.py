from utils.utils import curves_json_wrap, embedding_degree, increment_seed
from sage.all import ZZ, EllipticCurve, GF


def nums_curve(current_seed, prime: ZZ):
    b = ZZ(current_seed,16)
    cardinality = EllipticCurve(GF(prime), [-3, b]).__pari__().ellsea(1)
    cardinality = ZZ(cardinality)
    if cardinality == 0:
        return {}
    if not cardinality.is_prime():
        return {}
    twist_card = 2 * (prime + 1) - cardinality

    if prime <= cardinality:
        b = prime - b
        cardinality = twist_card

    if not twist_card.is_prime():
        return {}

    if not (cardinality - 1) / embedding_degree(prime=prime, order=cardinality) < 100:
        return {}
    t = prime + 1 - cardinality
    d = (t ** 2 - 4 * prime).squarefree_part()
    d = d if d % 4 == 1 else 4 * d
    if d.nbits() <= 100:
        return {}
    return {'a': prime - 3, 'b': b, 'order': cardinality, 'cofactor': 1}


def generate_nums_curves(count, p, seed):
    """Generates at most #count curves according to the standard
    """
    curves = []
    for i in range(1, count + 1):
        current_seed = increment_seed(seed, i)
        curve = nums_curve(current_seed, p)
        if curve:
            curve['generator'] = (ZZ(0), ZZ(0))
            curve['seed'] = current_seed
            curve['prime'] = p
            curves.append(curve)
    return curves_json_wrap(curves, p, count, seed, 'nums')
