from utils import SimulatedCurves
from x962_gen import X962


class NIST(X962):
    def __init__(self, seed, p, cofactor_bound=None, cofactor_div=0):
        super().__init__(seed, p, cofactor_bound, cofactor_div)
        self._standard = "nist"
        self._category = "nist"
        self._embedding_degree_bound = 100
        self._rmin = max(2 ** (self._p.nbits() - 1), 2 ** 160)


def generate_nist_curves(count, p, seed, cofactor_bound=None, cofactor_div=0):
    simulated_curves = SimulatedCurves("nist", p, seed, count)
    curve = NIST(seed, p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
    for _ in range(count):
        if not curve.secure():
            curve.seed_update()
            continue
        simulated_curves.add_curve(curve)
        curve = NIST(curve.seed(), p, cofactor_div=cofactor_div, cofactor_bound=cofactor_bound)
        curve.seed_update()
    return simulated_curves
