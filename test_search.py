import contextlib
import io
import tempfile
import unittest
import json
import random
from unittest.mock import patch
from pathlib import Path

import booker_sieve as solver
import hunt_unsolved as hunter


class SearchTests(unittest.TestCase):
    def test_singular_roots(self):
        self.assertEqual(sorted(solver.solve_cube_mod_d(24, 4)), [0, 2])
        self.assertEqual(solver.solve_cube_mod_d(3, 3), [0])
        self.assertEqual(sorted(solver.solve_cube_mod_d(732, 4)), [0, 2])
        self.assertEqual(sorted(solver.solve_cube_mod_d(975, 25)), [0, 5, 10, 15, 20])

    def test_zero_discriminant(self):
        self.assertEqual(solver.test_candidate(6, 2, 2), (-1, -1, 2))

    def test_modular_roots_against_enumeration(self):
        spf = solver.compute_spf(180)
        for k in range(-15, 31):
            for d in range(1, 181):
                expected = [z for z in range(d) if (z**3-k) % d == 0]
                self.assertEqual(sorted(solver.solve_cube_mod_d(k, d, spf)), expected, (k, d))

    def test_large_exact_candidates(self):
        triples = [
            (165, -385495523231271884, 383344975542639445, 98422560467622814),
            (579, 143075750505019222645, -143070303858622169975, -6941531883806363291),
            (906, -74924259395610397, 72054089679353378, 35961979615356503),
        ]
        for k, x, y, z in triples:
            found = solver.test_candidate(k, abs(x+y), z)
            self.assertIsNotNone(found)
            self.assertEqual(sum(t**3 for t in found), k)
            self.assertEqual(sorted(found), sorted((x, y, z)))
            band = solver.sieve_range_d(k,abs(z),abs(x+y),abs(x+y),z_min=abs(z))
            self.assertTrue(any(sorted(s) == sorted((x,y,z)) for s in band))
        # Arbitrarily large, synthetic exact solution with equal coordinates.
        n = 10**60
        self.assertEqual(solver.test_candidate(6*n**3, 2*n, 2*n), (-n, -n, 2*n))

    def test_full_small_boxes(self):
        B = 12
        cubes = {z**3: z for z in range(-B, B+1)}
        for k in range(-30, 61):
            if k in {i**3 for i in range(-4, 5)}:
                continue  # S=0 yields an infinite family outside this finite d engine.
            expected = set()
            for x in range(-B, B+1):
                for y in range(-B, B+1):
                    z = cubes.get(k-x**3-y**3)
                    if z is not None:
                        expected.add(tuple(sorted((x, y, z))))
            with contextlib.redirect_stdout(io.StringIO()):
                found = solver.sieve_range_d(k, B, 1, solver.max_divisor(k, B))
            actual = {tuple(sorted(s)) for s in found if max(map(abs, s)) <= B}
            self.assertEqual(actual, expected, k)

    def test_deep_three_primary_subgroups(self):
        for p in (109, 163, 487, 1459):
            for k in (0, 1, 3, 7, 24, 114, 579, 975, p-1):
                expected = [r for r in range(p) if (r**3-k) % p == 0]
                self.assertEqual(solver.solve_cube_mod_p(k,p), expected)

    def test_integer_bounds(self):
        for n in (0, 1, 2, 7, 8, 26, 27, 10**300, 10**300-1):
            r = solver.icbrt(n)
            self.assertLessEqual(r**3,n)
            self.assertGreater((r+1)**3,n)

    def test_constructed_solutions_with_large_signed_integers(self):
        rng = random.Random(114)
        for _ in range(1000):
            x,y,z = (rng.randrange(-10**30,10**30) for _ in range(3))
            if x+y == 0:
                continue
            k = x**3+y**3+z**3
            found = solver.test_candidate(k,abs(x+y),z)
            self.assertIsNotNone(found)
            self.assertEqual(sorted(found),sorted((x,y,z)))

    def test_split_intervals_and_large_band(self):
        k, B = 6, 40
        end = solver.max_divisor(k,B)
        full = set(solver.sieve_range_d(k,B,1,end))
        split = set(solver.sieve_range_d(k,19,1,end))
        split.update(solver.sieve_range_d(k,B,1,end,z_min=20))
        self.assertEqual(full,split)
        n = 10**30
        giant = solver.sieve_range_d(6*n**3,2*n,2*n,2*n,z_min=2*n)
        self.assertIn((-n,-n,2*n), giant)

    def test_checkpoint_resume_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                state = hunter.run_hunter_for_k(6,20,2,run_dir=tmp,chunk_size=3)
                again = hunter.run_hunter_for_k(6,20,2,run_dir=tmp,chunk_size=3)
            self.assertEqual(state,again)
            path = Path(tmp)/'k6.json'
            partial = dict(state)
            partial['last_d'] = 1
            partial['complete'] = False
            partial['solutions'] = [s for s in state['solutions'] if abs(s[0]+s[1]) <= 1]
            hunter.atomic_json(path,partial)
            with contextlib.redirect_stdout(io.StringIO()):
                resumed = hunter.run_hunter_for_k(6,20,2,run_dir=tmp,chunk_size=3)
            self.assertEqual(resumed['solutions'],state['solutions'])
            self.assertEqual(resumed['last_d'],state['last_d'])
            with self.assertRaisesRegex(ValueError,'mismatch'):
                hunter.run_hunter_for_k(6,21,2,run_dir=tmp)
            corrupt = dict(resumed)
            corrupt['solutions'] = [[0,0,0]]
            hunter.atomic_json(path,corrupt)
            with self.assertRaisesRegex(ValueError,'invalid checkpoint solution'):
                hunter.run_hunter_for_k(6,20,2,run_dir=tmp)

    def test_windows_checkpoint_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'cp.json'
            hunter.atomic_json(path,{'last_d':1})
            real_replace = hunter.os.replace
            calls = []
            def transient(a,b):
                calls.append(1)
                if len(calls) < 3:
                    self.assertEqual(json.loads(path.read_text())['last_d'],1)
                    raise PermissionError('transient sharing violation')
                return real_replace(a,b)
            with patch.object(hunter.os,'replace',side_effect=transient), patch.object(hunter.time,'sleep'):
                hunter.atomic_json(path,{'last_d':2})
            self.assertEqual(json.loads(path.read_text())['last_d'],2)
            self.assertEqual(len(calls),3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
