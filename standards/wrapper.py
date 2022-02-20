"""
Sage script containing the functions for the experiment.
Has CLI so we can start experiments directly from the CLI.

User can specify job to compute either via CLI or as
a JSON config file (not implemented here).

After experiment is finished, the script writes results to the output file.
"""

import argparse
import json
from sage.all import ZZ
from utils import IntegerEncoder


def main():
    parser = argparse.ArgumentParser(description="Sage experiment runner")

    parser.add_argument('--standard', help='which standard do you want to simulate')
    parser.add_argument("-c", "--count", action="store", help="")
    parser.add_argument("-p", "--prime", action="store", help="")
    parser.add_argument("-s", "--seed", action="store", help="")
    parser.add_argument("-u", "--cofactor", action="store", default=None, help="")
    parser.add_argument("-ud", "--cofactor_div", action="store", default=0, help="")
    parser.add_argument("-f", "--outfile", action="store", help="")
    args = parser.parse_args()
    gen_function = getattr(__import__(f"{args.standard}_gen"), f"generate_{args.standard}_curves")
    cofactor = ZZ(args.cofactor) if args.cofactor is not None else None
    c, p, s = ZZ(args.count), ZZ(args.prime), args.seed
    arguments = {"brainpool": (c, p, s), "c25519": (c, p, s), "nums": (c, p, s), "bls": (c, s), "bn": (c, s)}.get(
        args.standard, (
            c, p, s, cofactor, ZZ(args.cofactor_div)))
    results = gen_function(*arguments)
    with open(args.outfile, "w+") as f:
        json.dump(results.json_export(), f, indent=2, cls=IntegerEncoder)


if __name__ == "__main__":
    main()
