"""Bounded probes above 1000; local solutions do NOT imply worldwide novelty."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import booker_sieve as solver
from certify_lean import verify_triple

def main():
    B=10000
    records=[]
    for k in (1002,1005,1011,1014,1020,1023,1029):
        end=solver.max_divisor(k,B)
        found=solver.sieve_range_d(k,B,1,end,solver.compute_spf(end))
        unique=sorted({tuple(sorted(s)) for s in found})
        assert all(verify_triple(*s,k) for s in unique)
        records.append({'K':k,'B':B,'d_min':1,'d_max':end,'complete':True,
                        'triples_up_to_permutation':[list(s) for s in unique],
                        'novelty':'not assessed; no claim of a first published representation'})
        print(f'K={k}: {len(unique)} triples up to permutation, exact sums verified')
    output={'engine_sha256':hashlib.sha256((ROOT/'booker_sieve.py').read_bytes()).hexdigest(),
            'scope':'finite local probes, not a list of globally open cases',
            'records':records}
    (ROOT/'evidence'/'beyond-1000-probe.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
