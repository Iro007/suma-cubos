"""Exact finite divisor search, using arbitrary precision integers.
For S=x+y!=0: d=|S| divides k-z^3 and
Delta=3d(4|k-z^3|-d^3)=(3d(x-y))^2.
For |z|<=B, d<=floor_cuberoot(4(B^3+|k|)).
S=0 gives an infinite family only when k is a perfect cube.
No ordering assumptions or floating point bounds are used.
"""
from __future__ import annotations
import argparse
import array
import math
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
ALPHA = 2**(1/3)-1  # compatibility only; not a coverage bound
ENGINE_VERSION = 'exact-divisor-v2'
SQUARE_MODULI = (64,63,65,11,13,17,19)
SQUARE_TABLES = tuple(frozenset(x*x%m for x in range(m)) for m in SQUARE_MODULI)

def icbrt(n):
    if n < 0: raise ValueError('nonnegative input required')
    lo, hi = 0, 1 << ((n.bit_length()+2)//3)
    while lo < hi:
        mid = (lo+hi+1)//2
        if mid**3 <= n: lo = mid
        else: hi = mid-1
    return lo

def max_divisor(k,B):
    return icbrt(4*(B**3+abs(k)))

def ext_gcd(a,b):
    if b == 0: return a,1,0
    g,x,y = ext_gcd(b,a%b)
    return g,y,x-(a//b)*y

def mod_inv(a,m): return pow(a,-1,m)

def crt2(r1,m1,r2,m2):
    g,p,_ = ext_gcd(m1,m2)
    if (r2-r1)%g: return None,None
    L = m1*(m2//g)
    return (r1+((r2-r1)//g)*p*m1)%L,L

def compute_spf(limit):
    spf = array.array('I',range(limit+1))
    for p in range(2,math.isqrt(limit)+1):
        if spf[p] == p:
            for i in range(p*p,limit+1,p):
                if spf[i] == i: spf[i] = p
    return spf

def factor_integer(n,spf=None):
    result,p = [],2
    while n > 1:
        if spf is not None and n < len(spf): p = spf[n]
        else:
            while p*p <= n and n%p: p += 1 if p == 2 else 2
            if p*p > n: p = n
        e,pe = 0,1
        while n%p == 0:
            n //= p
            e += 1
            pe *= p
        result.append((p,pe,e))
    return result

@lru_cache(maxsize=100000)
def _prime_roots(k,p):
    if k == 0: return (0,)
    if p == 3: return (k,)
    if p%3 == 2: return (pow(k,(2*p-1)//3,p),)
    if pow(k,(p-1)//3,p) != 1: return ()
    # Invert cubing on the coprime part, then solve the 3-primary
    # subgroup discrete logarithm one ternary digit at a time.
    m,s = p-1,0
    while m%3 == 0:
        m //= 3
        s += 1
    g = 2
    while pow(g,(p-1)//3,p) == 1: g += 1
    c = pow(g,m,p)
    omega = pow(c,3**(s-1),p)
    r = pow(k,pow(3,-1,m),p) if m > 1 else 1
    residual = k*pow(pow(r,3,p),-1,p)%p
    j,power = 0,1
    for i in range(s):
        t = pow(residual,3**(s-1-i),p)
        digit = next(a for a in range(3) if pow(omega,a,p) == t)
        j += digit*power
        residual = residual*pow(pow(c,digit*power,p),-1,p)%p
        power *= 3
    if j%3: raise ArithmeticError('cube subgroup invariant failed')
    r = r*pow(c,j//3,p)%p
    roots = tuple(sorted({r,r*omega%p,r*omega*omega%p}))
    if any(pow(z,3,p) != k for z in roots): raise ArithmeticError('invalid prime root')
    return roots

def solve_cube_mod_p(k,p): return list(_prime_roots(k%p,p))

def _prime_power_roots(k,p,pe):
    roots,modulus = solve_cube_mod_p(k,p),p
    while modulus < pe:
        lifted = []
        for r in roots:
            f = ((r**3-k)//modulus)%p
            derivative = 3*r*r%p
            if derivative:
                lifted.append(r+(-f*pow(derivative,-1,p)%p)*modulus)
            elif f == 0:
                lifted.extend(r+t*modulus for t in range(p))
        roots,modulus = lifted,modulus*p
    return roots

def hensel_lift_cube(k,r,p,pe):
    roots = [z for z in _prime_power_roots(k,p,pe) if z%p == r]
    if len(roots) != 1: raise ValueError('root has zero or multiple lifts')
    return roots[0]

def solve_cube_mod_d(k,d,spf=None):
    if d < 1: raise ValueError('d must be positive')
    roots,modulus = [0],1
    for p,pe,_ in factor_integer(d,spf):
        local = _prime_power_roots(k,p,pe)
        if not local: return []
        roots = [crt2(a,modulus,b,pe)[0] for a in roots for b in local]
        modulus *= pe
    return roots

def test_candidate(k,d,z):
    if d <= 0: raise ValueError('d must be positive')
    diff = k-z**3
    delta = 3*d*(4*abs(diff)-d**3)
    if delta < 0: return None
    for m,residues in zip(SQUARE_MODULI,SQUARE_TABLES):
        if delta%m not in residues: return None
    root = math.isqrt(delta)
    if root*root != delta or root%(3*d): return None
    V,S = root//(3*d), d if diff > 0 else -d
    if (S+V)%2: return None
    x,y = (S+V)//2,(S-V)//2
    if abs(x) < abs(y): x,y = y,x
    if x**3+y**3+z**3 != k: return None
    return x,y,z

def sieve_range_d(k,B,d_min,d_max,spf=None,verbose=False,z_min=0):
    """All S!=0 solutions in the specified d and |z| rectangle."""
    if not 0 <= z_min <= B or d_min < 1 or d_max < d_min:
        raise ValueError('invalid search interval')
    if k%9 in (4,5): return []
    found = set()
    intervals = [(z_min,B),(-B,-max(1,z_min))]
    for d in range(d_min,min(d_max,max_divisor(k,B))+1):
        # A narrow band can be cheaper than materializing a huge set of
        # singular modular roots (e.g. k=0 mod p^e with large e).
        if 2*(B-z_min+1) < d:
            for low,high in intervals:
                for z in range(low,high+1):
                    if (z**3-k) % d == 0:
                        sol = test_candidate(k,d,z)
                        if sol is not None: found.add(sol)
            continue
        for r in solve_cube_mod_d(k,d,spf):
            for low,high in intervals:
                first = low+(r-low)%d
                for z in range(first,high+1,d):
                    sol = test_candidate(k,d,z)
                    if sol is not None: found.add(sol)
    return sorted(found)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--K',type=int,default=114)
    parser.add_argument('--B',type=int,default=100000)
    parser.add_argument('--z-min',type=int,default=0)
    parser.add_argument('--d-min',type=int,default=1)
    parser.add_argument('--d-max',type=int)
    parser.add_argument('--procs',type=int,default=1)
    parser.add_argument('--verbose',action='store_true')
    a = parser.parse_args()
    if a.B < 0 or a.procs < 1 or a.d_min < 1 or not 0 <= a.z_min <= a.B:
        parser.error('invalid bounds/process count')
    cap = max_divisor(a.K,a.B)
    end = min(a.d_max if a.d_max is not None else cap,cap)
    if end < a.d_min: parser.error('empty d interval')
    print(f'{ENGINE_VERSION}: K={a.K}, |z|=[{a.z_min},{a.B}], d=[{a.d_min},{end}]',flush=True)
    cube = icbrt(abs(a.K))
    if cube**3 == abs(a.K) and a.z_min <= cube <= a.B:
        z = cube if a.K >= 0 else -cube
        print(f'S=0 family: (t,-t,{z}), for every integer t')
    if a.procs == 1:
        found = sieve_range_d(a.K,a.B,a.d_min,end,compute_spf(end),z_min=a.z_min)
    else:
        width = max(1,(end-a.d_min+1+a.procs-1)//a.procs)
        tasks = [(a.K,a.B,d,min(end,d+width-1),None,False,a.z_min) for d in range(a.d_min,end+1,width)]
        with ProcessPoolExecutor(max_workers=a.procs) as pool:
            futures = [pool.submit(sieve_range_d,*t) for t in tasks]
            found = sorted({s for f in futures for s in f.result()})
    for sol in found: print(sol,'sum=',sum(x**3 for x in sol))
    print(f'completed; finite solutions={len(found)}; restricted ranges imply partial coverage')
    return 0

if __name__ == '__main__': raise SystemExit(main())
