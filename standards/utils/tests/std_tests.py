import json
from sage.all import Integer, ZZ
import x962.x962_gen as x962
import brainpool.brainpool_gen as brainpool
from utils.utils import int_to_hex_string


def test_x962_curve():
    """Testing of gen_curve on standardized x962 curves"""
    with open("test_x962_parameters.json", "r") as file:
        secg = json.load(file)
    for name, curve_dict in secg.items():
        nbits = Integer(name[4:-2])
        print(nbits)
        p = ZZ(curve_dict['p'], 16)
        res = x962.x962_curve(p, curve_dict['seed'], cofactor=0)
        assert res is not {}
        assert int_to_hex_string(p + res['a']) == curve_dict['A']
        assert int_to_hex_string(res['b']) == curve_dict['B'] or int_to_hex_string(p - res['b']) == curve_dict['B']
        assert int_to_hex_string(p) == curve_dict['p']


def test_brainpool_curve():
    """Testing of gen_curve on standardized Brainpool curves"""
    with open("testing_parameters_brainpool.json", "r") as file:
        brainpools = json.load(file)
    for nbits, curve_dict in brainpools.items():
        nbits = Integer(nbits)
        p = brainpool.gen_prime(curve_dict['prime_seed'], nbits)
        assert int_to_hex_string(p) == curve_dict['p']

        curve, gen, q = brainpool.brainpool_curve(p, curve_dict['seed'], nbits)
        x, y = Integer(gen[0]), Integer(gen[1])
        a, b = Integer(curve.a4()), Integer(curve.a6())

        def pad_zeros(hex_string):
            return (nbits // 4 - len(hex_string)) * "0" + hex_string
        assert int_to_hex_string(a) == pad_zeros(curve_dict['A'])
        assert int_to_hex_string(b) == pad_zeros(curve_dict['B'])
        assert int_to_hex_string(q) == pad_zeros(curve_dict['order'])
        assert int_to_hex_string(x) == pad_zeros(curve_dict['x'])


def test_generate_brainpool_curves():
    with open("testing_parameters_brainpool.json", "r") as f:
        params = json.load(f)
        for bits, curve in params.items():
            seed = curve["correct_seed"]
            p = Integer(int(curve["p"], 16))
            curves = brainpool.generate_brainpool_curves(5, Integer(p), seed)["curves"]
            print(bits)
            assert len(curves) == 1


if __name__ == '__main__':
    test_brainpool_curve()
    test_x962_curve()
    test_generate_brainpool_curves()
