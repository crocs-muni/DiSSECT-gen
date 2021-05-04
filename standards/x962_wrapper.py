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

from utils.json_handler import IntegerEncoder
from x962_gen import generate_x962_curves

def main():
    parser = argparse.ArgumentParser(description="Sage experiment runner")

    parser.add_argument("-c", "--count", action="store", help="")
    parser.add_argument("-p", "--prime", action="store", help="")
    parser.add_argument("-s", "--seed", action="store", help="")
    parser.add_argument("-u", "--cofactor", action="store", help="")
    parser.add_argument("-f", "--outfile", action="store", help="")
    parser.add_argument("--std_seed",action='store')
    args = parser.parse_args()
    r = generate_x962_curves(ZZ(args.count), ZZ(args.prime), args.seed, ZZ(args.cofactor),args.std_seed)

    # Save results to the output file
    with open(args.outfile, "w+") as fh:
        json.dump(r, fh, cls=IntegerEncoder)


if __name__ == "__main__":
    main()
