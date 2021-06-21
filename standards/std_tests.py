import json
from sage.all import Integer, ZZ

import x962_gen as x962
import brainpool_gen as brainpool
import nums_gen as nums
import nist_gen as nist
import secg_gen as secg


def test_x962_curve(bits=1000):
    """Testing of gen_curve on standardized x962 curves"""
    print("test_x962_curve")
    with open("parameters/test_parameters_x962.json", "r") as file:
        params = json.load(file)
    for name, curve_dict in params.items():
        nbits = curve_dict['bits']
        if nbits > bits:
            continue
        print("bits:", nbits)
        p = ZZ(curve_dict['p'])
        res = x962.x962_curve(curve_dict['seed'], p, cofactor=0)
        assert res != {}, "curve not found"
        assert res['a'] == ZZ(curve_dict['A']), 'parameter a is not correct'
        assert res['b'] == ZZ(curve_dict['B']) or p - res['b'] == ZZ(curve_dict['B']), 'parameter b is not correct'


def test_brainpool_curve(speedup=False, bits=1000):
    """Testing of gen_curve on standardized Brainpool curves"""
    print("test_brainpool_curve")
    with open("parameters/test_parameters_brainpool.json", "r") as file:
        brainpools = json.load(file)
    for nbits, curve_dict in brainpools.items():
        nbits = Integer(nbits)
        if nbits > bits:
            continue
        print('bits:', nbits)
        p = brainpool.gen_prime(curve_dict['prime_seed'], nbits)
        assert p == ZZ(curve_dict['p'])
        seed = curve_dict['correct_seed'] if speedup else curve_dict['seed']
        result = brainpool.brainpool_curve(p, seed, nbits)
        x, y = result['generator']
        a, b = result['a'], result['b']
        order = result['order']
        assert a == ZZ(curve_dict['A'])
        assert b == ZZ(curve_dict['B'])
        assert order == ZZ(curve_dict['order'])
        assert x == ZZ(curve_dict['x'])


def test_generate_brainpool_curves(bits=1000):
    """Testing of generate_brainpool_curves on standardize Brainpool curves"""
    print("test_generate_brainpool_curves")
    with open("parameters/test_parameters_brainpool.json", "r") as f:
        params = json.load(f)
        for nbits, curve in params.items():
            if Integer(nbits) > bits:
                continue
            seed = curve["correct_seed"]
            p = Integer(int(curve["p"]))
            curves = brainpool.generate_brainpool_curves(5, Integer(p), seed)["curves"]
            print(nbits)
            assert len(curves) == 1


def test_nums_curve(bits=1000):
    """Testing of gen_curve on standardized nums curve"""
    print("test_nums_curve")
    with open("parameters/test_parameters_nums.json", "r") as file:
        params = json.load(file)
    for name, curve_dict in params.items():
        nbits = curve_dict['bits']
        if nbits > bits:
            continue
        print("bits:", nbits)
        p = ZZ(curve_dict['p'])
        res = nums.nums_curve(curve_dict['seed'], p)
        assert res != {}, "curve not found"
        assert res['a'] == ZZ(curve_dict['A']), f"parameter a is not correct"
        assert res['b'] == ZZ(curve_dict['B']) or p - res['b'] == ZZ(curve_dict['B']), 'parameter b is not correct'


def test_nist_curve(bits=1000):
    """Testing of gen_curve on standardized nist curves"""
    print("test_nist_curve")
    with open("parameters/test_parameters_nist.json", "r") as file:
        params = json.load(file)
    for name, curve_dict in params.items():
        nbits = curve_dict['bits']
        if nbits > bits:
            continue
        print("bits:", nbits)
        p = ZZ(curve_dict['p'])
        res = nist.nist_curve(curve_dict['seed'], p)
        assert res != {}, "curve not found"
        assert res['a'] == ZZ(curve_dict['A']), 'parameter a is not correct'
        assert res['b'] == ZZ(curve_dict['B']) or p - res['b'] == ZZ(curve_dict['B']), 'parameter b is not correct'


def test_secg_curve(bits=1000):
    """Testing of gen_curve on standardized secg curves"""
    print("test_secg_curve")
    with open("parameters/test_parameters_secg.json", "r") as file:
        params = json.load(file)
    for name, curve_dict in params.items():
        nbits = curve_dict['bits']
        if nbits > bits:
            continue
        print("bits:", nbits)
        p = ZZ(curve_dict['p'])
        res = secg.sec_curve(curve_dict['seed'], p)
        assert res != {}, "curve not found"
        assert res['a'] == ZZ(curve_dict['A']), 'parameter a is not correct'
        assert res['b'] == ZZ(curve_dict['B']) or p - res['b'] == ZZ(curve_dict['B']), 'parameter b is not correct'


if __name__ == '__main__':
    bits = 300
    # test_brainpool_curve(speedup=True,bits=bits)
    test_x962_curve(bits)
    # test_generate_brainpool_curves(bits)
    # test_nums_curve(bits)
    # test_nist_curve(200)
    # test_secg_curve(bits)
