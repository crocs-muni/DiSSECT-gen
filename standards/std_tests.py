import json
from sage.all import Integer, ZZ

import x962_gen as x962
import brainpool_gen as brainpool
import utils.utils as utils


def test_x962_curve():
    """Testing of gen_curve on standardized x962 curves"""
    with open("parameters/test_parameters_x962.json", "r") as file:
        secg = json.load(file)
    for name, curve_dict in secg.items():
        nbits = Integer(name[4:-2])
        print("bits:", nbits)
        p = ZZ(curve_dict['p'], 16)
        res = x962.x962_curve(curve_dict['seed'],p, cofactor=0)
        assert res != {}, "curve not found"
        assert utils.int_to_hex_string(p + res['a']) == curve_dict['A'], 'parameter a is not correct'
        assert utils.int_to_hex_string(res['b']) == curve_dict['B'] or utils.int_to_hex_string(p - res['b']) == \
               curve_dict['B'], 'parameter b is not correct'
        assert utils.int_to_hex_string(p) == curve_dict['p'], 'underlying prime is not correct'


def test_brainpool_curve(speedup=False):
    """Testing of gen_curve on standardized Brainpool curves"""
    with open("parameters/test_parameters_brainpool.json", "r") as file:
        brainpools = json.load(file)
    for nbits, curve_dict in brainpools.items():
        nbits = Integer(nbits)
        print('bits:', nbits)
        p = brainpool.gen_prime(curve_dict['prime_seed'], nbits)
        assert utils.int_to_hex_string(p) == curve_dict['p']
        seed = curve_dict['correct_seed'] if speedup else curve_dict['seed']
        result = brainpool.brainpool_curve(p, seed, nbits)
        x, y = result['generator']
        a, b = result['a'], result['b']
        order = result['order']

        def pad_zeros(hex_string):
            return (nbits // 4 - len(hex_string)) * "0" + hex_string

        assert utils.int_to_hex_string(a) == pad_zeros(curve_dict['A'])
        assert utils.int_to_hex_string(b) == pad_zeros(curve_dict['B'])
        assert utils.int_to_hex_string(order) == pad_zeros(curve_dict['order'])
        assert utils.int_to_hex_string(x) == pad_zeros(curve_dict['x'])


def test_generate_brainpool_curves():
    """Testing of generate_brainpool_curves on standardize Brainpool curves"""
    with open("parameters/test_parameters_brainpool.json", "r") as f:
        params = json.load(f)
        for bits, curve in params.items():
            seed = curve["correct_seed"]
            p = Integer(int(curve["p"], 16))
            curves = brainpool.generate_brainpool_curves(5, Integer(p), seed)["curves"]
            print(bits)
            assert len(curves) == 1


if __name__ == '__main__':
    # test_brainpool_curve(speedup=False)
    test_x962_curve()
    # test_generate_brainpool_curves()
