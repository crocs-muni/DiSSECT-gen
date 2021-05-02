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
from brainpool_gen import generate_brainpool_curves

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sage experiment runner")

    parser.add_argument("-c", "--count", action="store", help="")
    parser.add_argument("-p", "--prime", action="store", help="")
    parser.add_argument("-s", "--seed", action="store", help="")
    parser.add_argument("-u", "--cofactor", action="store", help="")
    parser.add_argument("-f", "--outfile", action="store", help="")
    args = parser.parse_args()
    print(args)

    # Do the computation
    count = ZZ(args.count)
    p = ZZ(args.prime)
    seed = args.seed
    r = generate_brainpool_curves(count, p, seed)

    # Save results to the output file
    with open(args.outfile, "w+") as fh:
        json.dump(r, fh, cls=IntegerEncoder)
