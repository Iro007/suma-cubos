"""Exact searches over positive rationals and Gaussian integers.
Gaussian height is the maximum absolute integer component, not complex modulus.
No floating point operations are used. No worldwide novelty is asserted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path
from booker_sieve import icbrt

Gaussian = tuple[int,int]

def gaussian_multiply(u:Gaussian,v:Gaussian)->Gaussian:
    a,b=u; c,d=v
    return a*c-b*d,a*d+b*c

def gaussian_cube(u:Gaussian)->Gaussian:
    a,b=u
    return a**3-3*a*b*b,3*a*a*b-b**3

def gaussian_height(triple)->int:
    return max(abs(component) for value in triple for component in value)

def gaussian_cube_sum(triple)->Gaussian:
    cubes=[gaussian_multiply(gaussian_multiply(z,z),z) for z in triple]
    return sum(v[0] for v in cubes),sum(v[1] for v in cubes)

def positive_rational_numerators(k:int,q:int):
    if k<=0 or q<=0:
        raise ValueError('positive target and denominator required')
    target=k*q**3
    limit=icbrt(target)
    cubes={c**3:c for c in range(1,limit+1)}
    found=[]
    for a in range(1,limit+1):
        for b in range(a,limit+1):
            c=cubes.get(target-a**3-b**3)
            if c is not None and c>=b:
                found.append((a,b,c))
    return found

def rational_reference(k:int,q:int):
    limit=icbrt(k*q**3)
    return [s for s in combinations_with_replacement(range(1,limit+1),3)
            if sum(a**3 for a in s)==k*q**3]

def gaussian_solutions(k:int,height:int):
    if height<0:
        raise ValueError('nonnegative height required')
    values=[(a,b) for a in range(-height,height+1) for b in range(-height,height+1)]
    cubes=[gaussian_cube(z) for z in values]
    indexes=defaultdict(list)
    for j,v in enumerate(cubes):indexes[v].append(j)
    found=[]
    for i,u in enumerate(cubes):
        for j in range(i,len(cubes)):
            v=cubes[j]
            complement=(k-u[0]-v[0],-u[1]-v[1])
            for l in indexes.get(complement,()):
                if l>=j:
                    triple=(values[i],values[j],values[l])
                    if gaussian_cube_sum(triple)!=(k,0):
                        raise ArithmeticError('Gaussian verification failed')
                    found.append(triple)
    return sorted(found)

def gaussian_reference(k:int,height:int):
    """Different traversal: ordered pairs, third values indexed only by real part.
    Cubes are computed by repeated multiplication, not the expanded formula.
    """
    values=[(a,b) for a in range(-height,height+1) for b in range(-height,height+1)]
    cubes=[gaussian_multiply(gaussian_multiply(z,z),z) for z in values]
    by_real=defaultdict(list)
    for z,v in zip(values,cubes):by_real[v[0]].append((v[1],z))
    found=set()
    for x,u in zip(values,cubes):
        for y,v in zip(values,cubes):
            for imaginary,z in by_real.get(k-u[0]-v[0],()):
                if imaginary+u[1]+v[1]==0:
                    found.add(tuple(sorted((x,y,z))))
    return sorted(found)

def study(k:int,max_denominator:int,height:int):
    if max_denominator<1 or height<1:
        raise ValueError('positive search limits required')
    rationals=[]
    first=None
    for q in range(1,max_denominator+1):
        found=positive_rational_numerators(k,q)
        if found!=rational_reference(k,q):
            raise ArithmeticError('independent rational search mismatch')
        rationals.append({'denominator':q,'numerator_bound':icbrt(k*q**3),
                          'numerator_triples':found,'complete':True})
        if found and first is None:first=q
    gaussian=[]
    for H in (height-1,height):
        found=gaussian_solutions(k,H)
        reference=gaussian_reference(k,H)
        if found!=reference:
            raise ArithmeticError('independent Gaussian search mismatch')
        gaussian.append({'height':H,'complete':True,'independent_match':True,
                         'gaussian_values':(2*H+1)**2,
                         'unordered_pair_checks':((2*H+1)**2)*(((2*H+1)**2)+1)//2,
                         'triples_up_to_permutation':found})
    minimal=(not gaussian[0]['triples_up_to_permutation'] and bool(gaussian[1]['triples_up_to_permutation']))
    return {'K':k,'arithmetic':'exact integer and Fraction operations',
            'positive_rational_search':rationals,'minimal_positive_common_denominator':first,
            'gaussian_metric':'maximum absolute value of all six integer components',
            'gaussian_search':gaussian,'minimal_gaussian_height':height if minimal else None,
            'gaussian_minimality_status':'exhaustive computation with independent traversal; not a Lean nonexistence proof',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'novelty':'not assessed in the literature; no worldwide priority claim'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--K',type=int,default=114)
    p.add_argument('--max-denominator',type=int,default=6)
    p.add_argument('--gaussian-height',type=int,default=23)
    p.add_argument('--output',default='evidence/number-domains-k114.json')
    a=p.parse_args()
    result=study(a.K,a.max_denominator,a.gaussian_height)
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Minimum positive common denominator:',result['minimal_positive_common_denominator'])
    print('Minimum Gaussian component height:',result['minimal_gaussian_height'])
    for record in result['gaussian_search']:
        print('Gaussian height',record['height'],'triples',len(record['triples_up_to_permutation']))
    return 0

if __name__=='__main__':raise SystemExit(main())
