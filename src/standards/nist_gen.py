from utils import SimulatedCurves, curve_command_line
from x962_gen import X962


class NIST(X962):
    def __init__(self, seed, p, cofactor_bound=None, cofactor_div=0):
        super().__init__(seed, p, cofactor_bound, cofactor_div)
        self._standard = "nist"
        self._category = "nist"
        self._embedding_degree_bound = 100
        self._rmin = max(2 ** (self._p.nbits() - 1), 2 ** 160)


def generate_nist_curves(attempts, p, seed, cofactor_bound=None, cofactor_div=0, count=0):
    simulated_curves = SimulatedCurves("nist", p.nbits(), seed, attempts)
    curve = NIST(seed, p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
    a, c = 0, 0
    while (count == 0 and a < attempts) or (count > 0 and c < count):
        a += 1
        if not curve.secure():
            curve.seed_update()
            continue
        simulated_curves.add_curve(curve)
        c += 1
        curve = NIST(curve.seed(), p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
        curve.seed_update()
    return simulated_curves


if __name__ == "__main__":
    args = curve_command_line()
    results = generate_nist_curves(args.attempts, args.prime, args.seed, args.cofactor_bound, args.cofactor_div,
                                   args.count)
    results.to_json_file(args.outfile)
