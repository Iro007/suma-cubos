"""Read back the five published campaigns; never infer global nonexistence."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import booker_sieve as solver
from hunt_unsolved import load_checkpoint, UNSOLVED_TARGETS
CAMPAIGNS=[
('validated-v2-low-2026-10-10',0,10**6,1,1587401),
('validated-v2-high-2026-10-10',10**20,10**20+100000,1,10000),
('high20-extension-2026-10-10',10**20+100001,10**20+400000,1,10000),
('high20-divisors-2026-10-10',10**20,10**20+100000,10001,100000),
('high21-2026-10-10',10**21,10**21+100000,1,10000)]

def main():
    digest=hashlib.sha256((ROOT/'booker_sieve.py').read_bytes()).hexdigest()
    count=0
    for name,zmin,B,dmin,dmax in CAMPAIGNS:
        for k in UNSOLVED_TARGETS:
            config={'K':k,'B':B,'z_min':zmin,'d_min':dmin,'d_max':dmax,
                    'engine':solver.ENGINE_VERSION,'engine_sha256':digest}
            cp=ROOT/'experiments'/name/f'k{k}.json'
            state=load_checkpoint(cp,config)
            if not state['complete'] or state['last_d'] != dmax:
                raise ValueError(f'incomplete coverage: {name}, K={k}')
            if state['solutions']:
                raise ValueError(f'reported zero-solutions result changed: {name}, K={k}')
            count+=1
        print(f'{name}: 7/7 complete, matching parameters and engine hash, 0 triples')
    print(f'{count} completed campaign-target pairs verified. No global nonexistence claim.')

if __name__=='__main__': main()
