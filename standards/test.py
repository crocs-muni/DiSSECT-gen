import unittest
import json
import x962_gen as x962
import brainpool_gen as brainpool
import secg_gen as secg
import nums_gen as nums
import bls_gen as bls
from abc import ABC, abstractmethod
from sage.all import ZZ, EllipticCurve, GF


class CurveTests(ABC):

    def set_up(self, path, bits_bound=256):
        with open(path, "r") as file:
            curves = json.load(file)
        return {k: v for k, v in list(curves.items()) if bits_bound >= ZZ(v["bits"])}

    def curve_compare(self, p, curve, curve_dict):
        a, b = curve.a(), curve.b()
        ec = EllipticCurve(GF(p), [a, b])
        cofactor = curve.cofactor()
        self.assertTrue((ec.order() // cofactor).is_prime())
        self.assertEqual(a, ZZ(curve_dict['A']))
        B = ZZ(curve_dict['B'])
        self.assertEqual(b, min(B, p - B))
        self.assertEqual(curve.order(), ZZ(curve_dict['order']))
        self.assertEqual(curve.order(), ec.order() // cofactor)
        self.assertEqual(curve.cofactor(), ZZ(curve_dict["cofactor"]))
        try:
            properties = curve.properties()
            self.assertEqual(properties["j_invariant"], curve_dict["j"])
            self.assertEqual(properties["embedding_degree"], curve_dict["em"])
            self.assertEqual(properties["cm_discriminant"], curve_dict["cm"])
        except KeyError:
            pass

    @abstractmethod
    def generating_function(self):
        pass

    @abstractmethod
    def standard_class(self):
        pass

    def curves(self):
        return self._curves

    def standard(self):
        return self._standard

    def test_generate(self, seed_key='seed', offset=1, tries=2):
        for name, curve_dict in self.curves().items():
            seed = hex(ZZ(curve_dict[seed_key]) - offset)
            p = ZZ(curve_dict["p"])
            c, p, s = tries, ZZ(p), seed
            arguments = {"bls": (c, s)}.get(self.standard(), (c, p, s))
            curves = self.generating_function()(*arguments).curves()
            self.assertEqual(len(curves), 1)
            self.curve_compare(p, curves[0], curve_dict)

    def test_find_curve(self, slow=True):
        for name, curve_dict in self.curves().items():
            seed = curve_dict['seed'] if slow else curve_dict['correct_seed']
            p = ZZ(curve_dict["p"])
            curve = self.standard_class()(seed, p)
            curve.find_curve()
            self.curve_compare(p, curve, curve_dict)


class TestX962(unittest.TestCase, CurveTests):
    def setUp(self):
        self._curves = self.set_up("parameters/test_parameters_x962.json")
        self._standard = "x962"

    def standard_class(self):
        return x962.X962

    def generating_function(self):
        return x962.generate_x962_curves

    def test_generate_x962(self):
        self.test_generate()

    def test_find_x962(self):
        self.test_find_curve()

    def test_cofactor_4(self):
        curve_dict = self.curves()["cofactor4"]
        seed = curve_dict["seed"]
        p = ZZ(curve_dict["p"])
        curves = x962.generate_x962_curves(3, ZZ(p), seed, cofactor_bound=1, cofactor_div=1).curves()
        self.assertEqual(len(curves), 0)
        curves = x962.generate_x962_curves(3, ZZ(p), seed, cofactor_bound=4, cofactor_div=1).curves()
        self.assertEqual(len(curves), 0)
        curves = x962.generate_x962_curves(3, ZZ(p), seed, cofactor_bound=4, cofactor_div=2).curves()
        self.assertEqual(len(curves), 2)
        curve = x962.X962(seed, p, cofactor_bound=4, cofactor_div=2)
        curve.find_curve()
        self.curve_compare(p, curve, curve_dict)


class TestBrainpool(unittest.TestCase, CurveTests):

    def setUp(self):
        self._curves = self.set_up("parameters/test_parameters_brainpool.json")
        self._standard = "brainpool"

    def standard_class(self):
        return brainpool.Brainpool

    def generating_function(self):
        return brainpool.generate_brainpool_curves

    def test_prime(self):
        for name, curve_dict in self.curves().items():
            nbits = curve_dict['bits']
            p = brainpool.gen_brainpool_prime(curve_dict['prime_seed'], ZZ(nbits))
            self.assertEqual(p, ZZ(curve_dict['p']))

    def test_generate_brainpool(self):
        self.test_generate('correct_seed', offset=0, tries=10)

    def test_find_brainpool(self):
        self.test_find_curve(slow=False)


class TestSECG(unittest.TestCase, CurveTests):
    def setUp(self):
        self._curves = self.set_up("parameters/test_parameters_secg.json")
        self._standard = "secg"

    def standard_class(self):
        return secg.SECG

    def generating_function(self):
        return secg.generate_secg_curves

    def test_generate_sec(self):
        self.test_generate()

    def test_find_secg(self):
        self.test_find_curve()


class TestNUMS(unittest.TestCase, CurveTests):

    def setUp(self):
        self._curves = self.set_up("parameters/test_parameters_nums.json")
        self._standard = "nums"

    def standard_class(self):
        return nums.NUMS

    def generating_function(self):
        return nums.generate_nums_curves

    def test_generate_nums(self):
        self.test_generate()

    def test_find_nums(self):
        self.test_find_curve()


class TestBLS(unittest.TestCase, CurveTests):

    def setUp(self):
        self._curves = self.set_up("parameters/test_parameters_bls.json")
        self._standard = "bls"

    def standard_class(self):
        return bls.BLS

    def generating_function(self):
        return bls.generate_bls_curves

    def test_generate_bls(self):
        self.test_generate(offset=0)

    def test_find_bls(self):
        self.test_find_curve()


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
