from dissectgen.standards.utils import generate_curves, curve_command_line
from dissectgen.standards.x962_gen import X962


class NIST(X962):
    def __init__(self, seed, p, cofactor_bound=None, cofactor_div=0):
        super().__init__(seed, p, cofactor_bound=cofactor_bound, cofactor_div=cofactor_div)
        self._standard = "nist"
        self._category = "nist"
        self._embedding_degree_bound = 100
        self._rmin = max(2 ** (self._p.nbits() - 1), 2 ** 160)


def generate_nist_curves(attempts, p, seed, cofactor_bound=None, cofactor_div=0, count=0):
    """Generates at most #attempts curves according to the standard
    The cofactor is arbitrary if cofactor_one=False (default) otherwise cofactor=1
    """
    curve = NIST(seed, p, cofactor_bound=cofactor_bound, cofactor_div=cofactor_div)
    return generate_curves(attempts, count, curve)


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_nist_curves(args.attempts, args.prime, args.seed, args.cofactor_bound, args.cofactor_div,
                                   args.count)
    results.to_json_file(args.outfile)
