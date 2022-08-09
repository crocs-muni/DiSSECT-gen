import dissectgen.standards.pf_utils as pell
from sage.all import ZZ, QuadraticField, sqrt, divisors, log2, EllipticCurve_from_j, HilbertClassPolynomialDatabase, GF, \
    PolynomialRing


class NoHilbert(Exception):
    pass


# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.60.7340&rep=rep1&type=pdf

def pair_pn(x, y, T, U, D, p_min, p_max):
    g = QuadraticField(3 * D).gen()
    i = -1
    while True:
        i += 1
        xi, yi = (x + y * g) * (T + U * g) ** i
        if xi % 6 in [1, 5]:
            s = (xi - xi % 6) // 6
            p = 4 * s ** 2 + 1
        else:
            continue
        if p_min > p:
            continue
        if p > p_max:
            raise pell.NoSolution("p_max")
        if ZZ(p).is_prime():
            n1 = 4 * s ** 2 + 2 * s + 1
            n2 = 4 * s ** 2 - 2 * s + 1
        else:
            continue
        n = n1 if xi % 6 == 1 else n2
        if n.is_prime():
            continue
        return p, n


def secure_n(n):
    for d in divisors(n - 1):
        if log2(n) ** 2 < d < sqrt(n):
            return False
    for e in divisors(n + 1):
        if log2(n) ** 2 < e < sqrt(n):
            return False


def mnt(D_min, D_max, p_min, p_max):
    if D_min % 8 <= 3:
        D_min -= (D_min % 8 - 3)
    else:
        D_min += (11 - D_min % 8)

    D = D_min
    p,n,h = None, None, None
    while D < D_max:
        try:
            T, U = pell.pell_pm1(3 * D, 1)
            x, y = pell.Pell(3 * D, -8).solve()
            if not 0 <= x <= 2 * U * sqrt(2 * D) or not 2 * sqrt(2 / D) <= y <= 2 * T * sqrt(2 / D):
                D += 8

                continue
            solution = pair_pn(x, y, T, U, D, p_min, p_max)
            if solution is None:

                return None
            p, n = solution
            try:
                h = HilbertClassPolynomialDatabase()[-3 * D]
            except ValueError:
                D+=8

                continue
            break
        except pell.NoSolution as e:
            D += 8
            print(e)
            continue

    F = GF(p)
    h = PolynomialRing(F, 'x')(h)
    for j, e in h.roots():
        E = EllipticCurve_from_j(j)
        while True:
            G = E.random_point()
            if not G is E(0):
                break
        if n * G == E(0):
            return p, E, n, G


print(mnt(35, 5000, 0,2**1000))