from pf_utils import Pell, PQa
import json
from bn_gen import BN


def pqa_test():
    pqa = iter(PQa(0, 1, 13))
    for [x, y] in [[3, 4], [1, 3], [2, 3], [1, 4], [3, 1], [3, 4], [1, 3], [2, 3], [1, 4]]:
        a = next(pqa)
        assert (a["P"], a["Q"]) == (x, y)


def pell_test1():
    pell = iter(Pell(157, 12))
    for (x, y) in [(13, 1), (10663, 851), (579160, 46222), (483790960, 38610722), (26277068347, 2097138361),
                   (21950079635497, 1751807067011)]:
        assert next(pell) == (x, y)


def test_bn_gen():
    with open("parameters/test_parameters_bn.json", "r") as f:
        curves = json.load(f)
    for name, curve in curves.items():
        print(name)
        if curve["bits"] > 400:  # cm computation too time consuming otherwise
            continue
        seed = curve["seed"]
        initial_seed = int(seed, 16) + 5 * (-1) ** (int(seed, 16) > 0)
        found_curve = BN(hex(initial_seed))
        found_curve.find_curve()
        assert curve["bits"] == found_curve._bits
        assert curve["seed"] == found_curve.seed(), curve["seed"]
        assert int(curve["p"], 16) == found_curve._p
        assert int(curve["A"], 16) == found_curve._a
        assert int(curve["B"], 16) == found_curve._b
        assert int(curve["x"], 16) == int(found_curve.generator()[0], 16)
        assert int(curve["y"], 16) == int(found_curve.generator()[1], 16)
        assert int(curve["order"], 16) == found_curve.order()
        assert int(curve["j"], 16) == int(found_curve.properties()["j_invariant"], 16)
        assert int(curve["cm"], 16) == int(found_curve.properties()["cm_discriminant"], 16)
        assert int(curve["emb"], 16) == int(found_curve.properties()["embedding_degree"], 16)
        assert int(curve["cofactor"], 16) == found_curve.cofactor()


if __name__ == "__main__":
    test_bn_gen()
    print("success")
    # pqa_test()
    # pell_test1()
