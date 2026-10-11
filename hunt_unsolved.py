"""Run the exact solver with parameter-bound atomic JSON checkpoints.
A checkpoint advances only after a complete contiguous block is verified.
Changing K, B, z_min, divisor range or engine source requires a new run folder.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import booker_sieve as solver
from certify_lean import verify_triple
UNSOLVED_TARGETS = [114,390,627,633,732,921,975]
ROOT = Path(__file__).resolve().parent
_WORKER_SPF = None

def engine_digest():
    return hashlib.sha256((ROOT/'booker_sieve.py').read_bytes()).hexdigest()

def _init_worker(end):
    global _WORKER_SPF
    _WORKER_SPF = solver.compute_spf(end)

def _search_block(k,B,start,end,z_min):
    return solver.sieve_range_d(k,B,start,end,_WORKER_SPF,z_min=z_min)

def atomic_json(path,data):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:
        json.dump(data,f,indent=2,ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    # Antivirus/indexers/readers may transiently hold a Windows handle
    # without FILE_SHARE_DELETE. Preserve the old checkpoint and retry.
    for attempt in range(8):
        try:
            os.replace(tmp,path)
            break
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(min(0.05*2**attempt,0.5))

def load_checkpoint(path,config):
    path = Path(path)
    if not path.exists():
        return {'schema':2,'config':config,'last_d':config['d_min']-1,'solutions':[],
                'elapsed_seconds':0,'complete':False}
    state = json.loads(path.read_text(encoding='utf-8'))
    if state.get('schema') != 2 or state.get('config') != config:
        raise ValueError('checkpoint parameters/engine mismatch; use another --run-dir')
    last = state['last_d']
    if not isinstance(last,int) or not config['d_min']-1 <= last <= config['d_max']:
        raise ValueError('invalid checkpoint progress')
    if bool(state['complete']) != (last == config['d_max']):
        raise ValueError('inconsistent checkpoint completion')
    for sol in state['solutions']:
        if len(sol) != 3 or any(type(x) is not int for x in sol):
            raise ValueError('invalid checkpoint triple')
        x,y,z = sol
        if not verify_triple(x,y,z,config['K']):
            raise ValueError('invalid checkpoint solution')
        if not config['z_min'] <= abs(z) <= config['B'] or not config['d_min'] <= abs(x+y) <= last:
            raise ValueError('solution outside committed checkpoint coverage')
    return state

def run_hunter_for_k(k,B,threads=4,d_min=1,d_max=None,z_min=0,
                     run_dir='experiments/exact-search',chunk_size=2048):
    if B < 0 or not 0 <= z_min <= B or threads < 1 or chunk_size < 1 or d_min < 1:
        raise ValueError('invalid bounds/process count/block size')
    if solver.icbrt(abs(k))**3 == abs(k):
        raise ValueError('K is a cube; S=0 has an infinite family; use booker_sieve.py directly')
    end = min(d_max if d_max is not None and d_max != -1 else solver.max_divisor(k,B),
              solver.max_divisor(k,B))
    if end < d_min: raise ValueError('empty divisor interval')
    if end > 10000000:
        raise ValueError('SPF resource limit: specify --d-max <= 10000000 for a partial search')
    config = {'K':k,'B':B,'z_min':z_min,'d_min':d_min,'d_max':end,
              'engine':solver.ENGINE_VERSION,'engine_sha256':engine_digest()}
    folder = Path(run_dir).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    cp = folder/f'k{k}.json'
    state = load_checkpoint(cp,config)
    if state['complete']:
        print(f'K={k}: already complete; solutions={len(state["solutions"])}',flush=True)
        return state
    atomic_json(cp,state)
    print(f'K={k}: |z|=[{z_min},{B}], d=[{d_min},{end}], resume_d={state["last_d"]+1}',flush=True)
    start_time = time.perf_counter()
    previous_elapsed = state['elapsed_seconds']
    known = {tuple(s) for s in state['solutions']}
    start = state['last_d']+1
    with ProcessPoolExecutor(max_workers=threads,initializer=_init_worker,initargs=(end,)) as pool:
        while start <= end:
            # Bounded in-flight queue, consumed in order: never checkpoint holes.
            window = []
            for _ in range(2*threads):
                if start > end: break
                stop = min(end,start+chunk_size-1)
                f = pool.submit(_search_block,k,B,start,stop,z_min)
                window.append((start,stop,f))
                start = stop+1
            for lo,hi,f in window:
                result = f.result()  # worker failure leaves last committed prefix intact
                for sol in result:
                    if not verify_triple(*sol,k):
                        raise ArithmeticError('independent verification failed')
                    if not lo <= abs(sol[0]+sol[1]) <= hi or not z_min <= abs(sol[2]) <= B:
                        raise ArithmeticError('worker result outside its assigned interval')
                    known.add(tuple(sol))
                state['solutions'] = [list(s) for s in sorted(known)]
                state['last_d'] = hi
                state['complete'] = hi == end
                state['elapsed_seconds'] = previous_elapsed+time.perf_counter()-start_time
                atomic_json(cp,state)
    print(f'K={k}: COMPLETE; d={d_min}..{end}; seconds={state["elapsed_seconds"]:.2f}; solutions={len(known)}',flush=True)
    return state

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--K',type=int)
    p.add_argument('--all',action='store_true')
    p.add_argument('--B',type=int,default=100000)
    p.add_argument('--z-min',type=int,default=0)
    p.add_argument('--d-min',type=int,default=1)
    p.add_argument('--d-max',type=int)
    p.add_argument('--threads','--procs',type=int,default=4)
    p.add_argument('--chunk-size',type=int,default=2048)
    p.add_argument('--run-dir',default='experiments/exact-search')
    a = p.parse_args()
    if a.all and a.K is not None: p.error('choose --all or --K')
    targets = UNSOLVED_TARGETS if a.all else [a.K if a.K is not None else 114]
    try:
        for k in targets:
            run_hunter_for_k(k,a.B,a.threads,a.d_min,a.d_max,a.z_min,a.run_dir,a.chunk_size)
    except (ValueError,ArithmeticError,OSError) as e:
        p.exit(2,f'ERROR: {e}\n')
    return 0

if __name__ == '__main__': raise SystemExit(main())
