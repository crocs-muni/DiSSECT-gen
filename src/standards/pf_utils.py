from sage.all import ZZ, sqrt, floor, PolynomialRing, RR, ceil


class NoSolution(Exception):
    pass


# PQa algorithm
# From John P. Robertson "Solving the generalized Pell equation"
class PQa:
    def __init__(self, P, Q, D):
        self._P = P
        self._Q = Q
        self._D = D
        self._a = floor((P + sqrt(D)) / Q)
        self._i = 0
        self._A1, self._A2 = ZZ(1), ZZ(self._a)
        self._B1, self._B2 = ZZ(0), ZZ(1)
        self._G1, self._G2 = Q, self._a * Q - P
        self._period = None  # the length l of the period
        self._preperiod = None  # starting index of the first period
        self._preperiod_PQ = None

    def __iter__(self):
        return self

    def _rec(self, X, Y):
        return self._a * X + Y, X

    def result(self):
        return {"P": self._P, "Q": self._Q, "B": self._B1, "G": self._G1, "a": self._a, "i": self._i,
                "period": self._period, "preperiod": self._preperiod}

    def _reduce_check(self):
        # checks whether the first period started
        if self._preperiod is not None:
            return
        if (self._P + sqrt(self._D)) / self._Q > 1 and 0 > (self._P - sqrt(self._D)) / self._Q > -1:
            self._preperiod = self._i
            self._preperiod_PQ = self._P, self._Q

    def _period_check(self):
        # checks whether the first period ended
        if self._preperiod is None or self._i <= self._preperiod:
            return
        if (self._P, self._Q) == self._preperiod_PQ:
            self._period = self._i - self._preperiod

    def __next__(self):
        self._i += 1
        self._P = self._a * self._Q - self._P  # Pi
        self._Q = (self._D - self._P ** 2) // self._Q  # Qi

        self._a = floor((self._P + sqrt(self._D)) / self._Q)  # a_i

        self._A2, self._A1 = self._rec(self._A2, self._A1)  # A_i, A_{i-1}
        self._B2, self._B1 = self._rec(self._B2, self._B1)  # B_i, B_{i-1}
        self._G2, self._G1 = self._rec(self._G2, self._G1)  # G_i, G_{i-1}

        self._reduce_check()  # checks whether the first period started
        self._period_check()  # checks whether the first period ended

        return self.result()  # return Pi, Qi, B_{i-1}, G_{i-1}, a_i, i


# Solves x^2-D*y^2=N where N=\pm 1 using alg. from John P. Robertson "Solving the generalized Pell equation", page 8
# Returns only the minimal solution
# ISO wants the solution with minimal y which is the same (at least in this case)
def pell_pm1(D, N=1):
    l = None
    D = ZZ(D)
    if D.is_square():
        raise NoSolution("D square")
    solution_index = None
    for res in iter(PQa(ZZ(0), ZZ(1), ZZ(D))):
        if res["Q"] == 1:
            l = res["i"]
            if N == 1 and l % 2 == 0:
                solution_index = l
            if N == 1 and l % 2 != 0:
                solution_index = l
            if N == -1 and l % 2 != 0:
                solution_index = l
            if N == -1 and l % 2 == 0:
                return None

        if l is not None and res["i"] == solution_index:
            return res["G"], res["B"]

        if l is not None and res["i"] == solution_index:
            return res["G"], res["B"]


# Pell equation (x^2-Dy^2=N) solver from John P. Robertson "Solving the generalized Pell equation", page 15
# Assuming N^2<D, D is non-square
class Pell:
    def __init__(self, D, N):
        self._N = ZZ(N)
        self._D = ZZ(D)
        assert N != 0 and D > 0 and not ZZ(D).is_square()
        assert N ** 2 < D, "not implemented"
        self._pqa = None
        self._solvable = None

    def __iter__(self):
        self._pqa = iter(PQa(ZZ(0), ZZ(1), self._D))
        return self

    def __next__(self):
        if self._solvable is not None and not self._solvable:
            raise NoSolution("No solution pell")

        if self._N in [1, -1]:
            return pell_pm1(self._D, self._N)

        while True:
            pqa = next(self._pqa)

            # iff condition on solvability from https://mathworld.wolfram.com/PellEquation.html
            if pqa["period"] is not None and self._solvable is None:
                self._solvable = False
                raise NoSolution("No solution pell")
            if pqa["Q"] * (-1) ** (pqa["i"] % 2) == self._N:
                self._sovable = True

            g, b = pqa["G"], pqa["B"]
            if self._N % (g ** 2 - self._D * b ** 2) == 0:
                f = self._N // (g ** 2 - self._D * b ** 2)
                if not f.is_square():
                    continue
                f = ZZ(sqrt(f))
                self._solvable = True
                return f * g, f * b

    def solve(self):
        return next(iter(self))


# finds initial seed for BN
def find_u(bits):
    x = PolynomialRing(ZZ, 'x').gen()
    P = 36 * x ** 4 + 36 * x ** 3 + 24 * x ** 2 + 6 * x + 1
    f = P(-x) - 2 ** (bits - 1)
    return ceil(f.roots(RR)[-1][0])


