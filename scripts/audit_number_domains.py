"""Compare a fresh exact replay with the published number-domain study."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'evidence/number-domains-k114.json').read_text(encoding='utf-8'))
replayed=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
if replayed!=expected:
    raise SystemExit('Number-domain replay differs from published evidence')
print('Exact replay matches all rational and Gaussian results, including source fingerprint.')
