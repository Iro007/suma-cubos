import unittest
from itertools import combinations_with_replacement
from fractions import Fraction
import number_domains as domains

class NumberDomainTests(unittest.TestCase):
    def test_rational_denominator_minimum(self):
        for q in range(1,7):
            expected=[] if q<6 else [(13,14,27)]
            self.assertEqual(domains.positive_rational_numerators(114,q),expected)
            self.assertEqual(domains.rational_reference(114,q),expected)
        triple=(Fraction(13,6),Fraction(7,3),Fraction(9,2))
        self.assertEqual(sum(x**3 for x in triple),114)
        self.assertTrue(all(x>0 for x in triple))

    def test_gaussian_cube_formula(self):
        for a in range(-12,13):
            for b in range(-12,13):
                z=(a,b)
                self.assertEqual(domains.gaussian_cube(z),domains.gaussian_multiply(domains.gaussian_multiply(z,z),z))

    def test_small_gaussian_boxes_against_triple_enumeration(self):
        for H in range(3):
            values=[(a,b) for a in range(-H,H+1) for b in range(-H,H+1)]
            for k in (-5,0,1,3,6,114):
                expected=[s for s in combinations_with_replacement(values,3)
                          if domains.gaussian_cube_sum(s)==(k,0)]
                self.assertEqual(domains.gaussian_solutions(k,H),expected)
                self.assertEqual(domains.gaussian_reference(k,H),expected)

    def test_gaussian_minimum_and_witness(self):
        self.assertEqual(domains.gaussian_solutions(114,22),[])
        witness=((-23,-10),(-23,10),(22,0))
        self.assertEqual(domains.gaussian_solutions(114,23),[witness])
        self.assertEqual(domains.gaussian_cube_sum(witness),(114,0))
        self.assertEqual(domains.gaussian_height(witness),23)

    def test_invalid_search_bounds(self):
        for k,q in ((0,1),(114,0),(-1,2)):
            with self.assertRaises(ValueError):domains.positive_rational_numerators(k,q)
        with self.assertRaises(ValueError):domains.gaussian_solutions(114,-1)

if __name__=='__main__':unittest.main(verbosity=2)
