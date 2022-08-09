import json
from dissectgen.standards.bn_gen import BN


def test_bn_gen():
    with open("test_parameters/test_parameters_bn.json", "r") as f:
        curves = json.load(f)
    for name, curve in curves.items():
        print(name)
        if curve["bits"] > 400:  # cm computation too time-consuming otherwise
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
