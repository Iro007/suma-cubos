"""Bounded probes above 1000; local solutions do NOT imply worldwide novelty."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import booker_sieve as solver
from certify_lean import verify_triple

HISTORICAL_REFERENCE_URL='https://www.asahi-net.or.jp/~KC2H-MSM/mathland/math04/matb0111.htm'
HISTORICAL_REFERENCE_TRIPLES={
    1002:(1,1,10),1005:(-193,-319,341),1014:(1040,1529,-1675),
    1023:(-1,8,8),1029:(-104,-140,157)}

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
        record=records[-1]
        record['historical_reference_url']=HISTORICAL_REFERENCE_URL
        reference=HISTORICAL_REFERENCE_TRIPLES.get(k)
        if reference is not None:
            assert verify_triple(*reference,k)
            assert tuple(sorted(reference)) in unique
            record['target_previously_represented']=True
            record['historical_reference_triple']=list(reference)
            record['novelty']='target already represented in the historical table; no new-target discovery'
        else:
            record['target_previously_represented']='not established by this historical table'
            record['novelty']='empty historical entry and local bounded search are not proof of worldwide open status'
        print(f'K={k}: {len(unique)} triples up to permutation, exact sums verified')
    output={'engine_sha256':hashlib.sha256((ROOT/'booker_sieve.py').read_bytes()).hexdigest(),
            'scope':'finite local probes, not a list of globally open cases',
            'records':records}
    (ROOT/'evidence'/'beyond-1000-probe.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
