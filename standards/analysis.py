from utils.utils import embedding_degree, increment_seed
from sage.all import EllipticCurve, GF

import argparse
from sage.all import ZZ

from utils.json_handler import save_into_json
from nums_gen import generate_nums_curves


def nums_curve(current_seed, prime: ZZ):
    b = ZZ(current_seed,16)
    try:
        cardinality = EllipticCurve(GF(prime), [-3, b]).__pari__().ellsea(1)
    except ArithmeticError:
        return {'fail':'disc'}
    cardinality = ZZ(cardinality)
    if cardinality == 0:
        return {'fail':'prime'}
    if not cardinality.is_prime():
        return {'fail':'prime'}
    twist_card = 2 * (prime + 1) - cardinality
    if prime <= cardinality:
        b = prime - b
        cardinality = twist_card

    if not twist_card.is_prime():
        return {'fail':'twistprime'}

    if not (cardinality - 1) / embedding_degree(prime=prime, order=cardinality) < 100:
        return {'fail':'mov'}

    d = ((prime + 1 - cardinality)**2-4*prime)
    if d.nbits() <= 100:
        return {'fail':'cmdisc'}
    return {'a': prime - 3, 'b': b, 'order': cardinality, 'cofactor': 1}


def generate_nums_curves(count, p, seed):
    """Generates at most #count curves according to the standard
    """
    curves = []
    for i in range(1, count + 1):
        current_seed = increment_seed(seed, i)
        curve = nums_curve(current_seed, p)
        curve['seed'] = current_seed
        curve['prime'] = p
        curves.append(curve)
    return {'curves':curves, 'prime':p, 'count':count, 'seed':seed, 'category':'nums'}



def main():
    parser = argparse.ArgumentParser(description="Sage experiment runner")

    parser.add_argument("-c", "--count", action="store", help="")
    parser.add_argument("-p", "--prime", action="store", help="")
    parser.add_argument("-s", "--seed", action="store", help="")
    parser.add_argument("-u", "--cofactor", action="store", help="")
    parser.add_argument("-f", "--outfile", action="store", help="")
    args = parser.parse_args()
    results = generate_nums_curves(ZZ(args.count), ZZ(args.prime), args.seed)
    save_into_json(results, args.outfile, mode="w+")


if __name__ == "__main__":
    main()
