from dissectgen.standards import x962_gen, secg_gen, nums_gen, c25519_gen, nist_gen, brainpool_gen, random_gen, bn_gen
from dissectgen.standards.utils import increment_seed
from sage.all import ZZ
import json

X962_PATH = "test_parameters/test_parameters_x962.json"
SECG_PATH = "test_parameters/test_parameters_secg.json"
NUMS_PATH = "test_parameters/test_parameters_nums.json"
NIST_PATH = "test_parameters/test_parameters_nist.json"
C25519_PATH = "test_parameters/test_parameters_c25519.json"
BRAINPOOL_PATH = "test_parameters/test_parameters_brainpool.json"
RANDOM_PATH = "test_parameters/test_parameters_random.json"
BN_PATH = "test_parameters/test_parameters_bn.json"


def find_verifiable_curve(gen, path, bits_bound, offset=5):
    with open(path, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > bits_bound:
            break
        p = ZZ(curve_dict["p"])
        seed = increment_seed(curve_dict["seed"], - offset)
        curve = gen(seed, p)
        curve.find_curve()
        assert curve.a() == ZZ(curve_dict["A"])
        assert curve.b() == ZZ(curve_dict["B"])


def test_find_curve_x962():
    find_verifiable_curve(x962_gen.X962, X962_PATH, 120)


def test_find_curve_secg():
    find_verifiable_curve(secg_gen.SECG, SECG_PATH, 120)


def test_find_curve_nums():
    find_verifiable_curve(nums_gen.NUMS, NUMS_PATH, 170)


def test_find_curve_nist():
    find_verifiable_curve(nist_gen.NIST, NIST_PATH, 170)


def test_find_curve_c25519():
    find_verifiable_curve(c25519_gen.C25519, C25519_PATH, 200)


def test_find_curve_brainpool():
    find_verifiable_curve(brainpool_gen.Brainpool, BRAINPOOL_PATH, 170, offset=-282)


def test_find_curve_random():
    with open(RANDOM_PATH, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > 120:
            break
        seed = curve_dict["seed"]
        curve = random_gen.RandomEC(seed, bits)
        curve.find_curve()
        assert curve.a() == ZZ(curve_dict["A"])
        assert curve.b() == ZZ(curve_dict["B"])


def test_find_curve_bn():
    with open(BN_PATH, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > 200:
            break
        seed = curve_dict["seed"]
        curve = bn_gen.BN(seed)
        curve.find_curve()
        assert curve.a() == ZZ(curve_dict["A"])
        assert curve.b() == ZZ(curve_dict["B"])


def generate_verifiable_curves(gen, args, path, bits_bound, seed_key="seed", offset=2):
    with open(path, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > bits_bound:
            break
        p = ZZ(curve_dict["p"])
        seed = increment_seed(curve_dict[seed_key], -offset)
        curves = gen(5, p, seed, **args).curves()
        assert len(curves) == 1


def test_generate_x962_curves():
    generate_verifiable_curves(x962_gen.generate_x962_curves, dict(cofactor_bound=None, cofactor_div=0), X962_PATH, 120)


def test_generate_secg_curves():
    generate_verifiable_curves(secg_gen.generate_secg_curves, dict(), SECG_PATH, 120)


def test_generate_nums_curves():
    generate_verifiable_curves(nums_gen.generate_nums_curves, dict(), NUMS_PATH, 170)


def test_generate_nist_curves():
    generate_verifiable_curves(nist_gen.generate_nist_curves, dict(cofactor_bound=None, cofactor_div=0), NIST_PATH, 170)


def test_generate_c25519_curves():
    generate_verifiable_curves(c25519_gen.generate_c25519_curves, dict(), C25519_PATH, 200)


def test_generate_brainpool_curves():
    generate_verifiable_curves(brainpool_gen.generate_brainpool_curves, dict(), BRAINPOOL_PATH, 170,
                               seed_key="correct_seed", offset=0)


def test_generate_random_curves():
    with open(RANDOM_PATH, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > 120:
            break
        seed = curve_dict["seed"]
        curves = random_gen.generate_random_curves(14, bits, seed).curves()
        assert len(curves) == 1


def test_generate_bn_curves():
    with open(BN_PATH, "r") as f:
        parameters = json.load(f)
    for name, curve_dict in parameters.items():
        bits = curve_dict["bits"]
        if bits > 120:
            break
        seed = curve_dict["seed"]
        curves = bn_gen.generate_bn_curves(5, seed).curves()
        assert len(curves) == 1
