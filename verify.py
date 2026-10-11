#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — Independent checker for any claimed solution to x^3+y^3+z^3=114.

Usage:
  python verify.py 1 2 3          # checks a single triple
  python verify.py solutions.txt  # checks one triple per line (x y z)
"""
from __future__ import annotations
import sys

K = 114


def icbrt(n: int) -> tuple[int, bool]:
    if n == 0:
        return 0, True
    neg = n < 0
    a = -n if neg else n
    try:
        m = int(round(a ** (1.0 / 3.0)))
    except OverflowError:
        m = 1 << (a.bit_length() // 3 + 1)
    while (m + 1) ** 3 <= a:
        m += 1
    while m ** 3 > a:
        m -= 1
    for cand in (m - 2, m - 1, m + 1, m + 2):
        if cand >= 0 and cand ** 3 == a:
            m = cand
            break
    return (-m if neg else m), (m ** 3 == a)


def verifica(x: int, y: int, z: int, K_val: int = K) -> bool:
    return x ** 3 + y ** 3 + z ** 3 == K_val


def chequeo_SV(x: int, y: int, z: int, K_val: int = K) -> bool:
    S = x + y
    V = x - y
    return 3 * S * V * V == 4 * (K_val - z ** 3) - S ** 3


def check_triple(x: int, y: int, z: int, K_val: int = K) -> tuple[bool, str]:
    ok1 = verifica(x, y, z, K_val)
    ok2 = chequeo_SV(x, y, z, K_val)
    if ok1 and ok2:
        return True, f"✅ VALID: {x}^3 + {y}^3 + {z}^3 = {x**3 + y**3 + z**3} (K={K_val})"
    else:
        return False, (f"❌ INVALID: sum={x**3 + y**3 + z**3} (target {K_val}), "
                       f"SV_check={ok2}")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Verificador exacto de ternas para x^3+y^3+z^3=K")
    parser.add_argument("args", nargs="*", help="x y z [K], o nombre de archivo")
    parser.add_argument("--K", "-k", type=int, default=None, help="Valor objetivo K (default: 114)")
    parsed = parser.parse_args()

    target_K = parsed.K if parsed.K is not None else K

    if not parsed.args:
        print(__doc__)
        return 1

    if len(parsed.args) in (3, 4):
        # x y z [K]
        x, y, z = map(int, parsed.args[:3])
        if len(parsed.args) == 4 and parsed.K is None:
            target_K = int(parsed.args[3])
        ok, msg = check_triple(x, y, z, target_K)
        print(msg)
        return 0 if ok else 1

    # file with triples
    fname = sys.argv[1]
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]
    except FileNotFoundError:
        print(f"File not found: {fname}")
        return 1

    print(f"Checking {len(lines)} candidate(s) from {fname}...")
    all_ok = True
    for i, ln in enumerate(lines, 1):
        try:
            x, y, z = map(int, ln.split())
        except ValueError:
            print(f"  Line {i}: malformed -> {ln}")
            all_ok = False
            continue
        ok, msg = check_triple(x, y, z)
        print(f"  {i:3d}: {msg}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\n🎉 All candidates verify correctly.")
    else:
        print("\n⚠️  Some candidates failed verification.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())