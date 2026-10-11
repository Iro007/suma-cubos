#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
certify_lean.py — Generador de Certificados de Prueba Formal en Lean 4
====================================================================
Genera un certificado matemático formal verificable por computadora en Lean 4
para cualquier solución diofántica x^3 + y^3 + z^3 = K.

Uso:
    python certify_lean.py -5 4 4 --K 3
    python certify_lean.py -435203231 435203083 4381159 --K 75
    python certify_lean.py solutions.txt
"""

from __future__ import annotations
import argparse
import sys
import os
from typing import Tuple


def verify_triple(x: int, y: int, z: int, k: int) -> bool:
    """Verificación exacta en aritmética de enteros de precisión arbitraria."""
    return x ** 3 + y ** 3 + z ** 3 == k


def generate_lean_code(x: int, y: int, z: int, k: int) -> str:
    """Genera el código fuente de Lean 4 para el teorema."""
    theorem_name = f"solution_sum_three_cubes_k{abs(k)}"
    return f"""-- ==============================================================================
-- Formal Lean 4 Certificate for the Diophantine Equation x^3 + y^3 + z^3 = {k}
-- Generated automatically by certify_lean.py
-- ==============================================================================

import Mathlib.Data.Int.Basic

/--
  Teorema formal: la terna (x, y, z) es una solución exacta a la
  ecuación diofantina de la suma de tres cubos para K = {k}.
-/
theorem {theorem_name} :
    (({x} : ℤ) ^ 3) + (({y} : ℤ) ^ 3) + (({z} : ℤ) ^ 3) = ({k} : ℤ) := by
  decide

#eval (({x} : ℤ) ^ 3) + (({y} : ℤ) ^ 3) + (({z} : ℤ) ^ 3)
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generador de certificados Lean 4 para x^3+y^3+z^3=K")
    parser.add_argument("args", nargs="*", help="x y z o archivo de soluciones")
    parser.add_argument("--K", "-k", type=int, default=114, help="Valor objetivo K (default: 114)")
    parser.add_argument("--out", "-o", type=str, default=None, help="Archivo .lean de salida")
    parsed = parser.parse_args()

    if not parsed.args:
        print(__doc__)
        return 1

    if len(parsed.args) >= 3:
        x, y, z = map(int, parsed.args[:3])
        k = parsed.K
        if len(parsed.args) >= 4:
            k = int(parsed.args[3])

        print(f"[*] Verificando aritméticamente: ({x})³ + ({y})³ + ({z})³ == {k}...")
        if not verify_triple(x, y, z, k):
            print(f"❌ Error: La terna no suma {k} (suma = {x**3 + y**3 + z**3}).")
            return 1
        print("✅ Verificación exacta en Python exitosa.")

        lean_code = generate_lean_code(x, y, z, k)
        out_name = parsed.out or f"Solution_K{k}.lean"
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(lean_code)

        print(f"🎉 Certificado formal Lean 4 generado en: {out_name}")
        print("\n--- Contenido del Certificado ---")
        print(lean_code)
        return 0

    # Archivo con ternas
    fname = parsed.args[0]
    if not os.path.exists(fname):
        print(f"Archivo no encontrado: {fname}")
        return 1

    with open(fname, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

    print(f"Procesando {len(lines)} candidatos desde {fname}...")
    for idx, ln in enumerate(lines, 1):
        parts = ln.split()
        if len(parts) < 3:
            continue
        x, y, z = map(int, parts[:3])
        k = parsed.K
        if verify_triple(x, y, z, k):
            out_file = f"Solution_K{k}_{idx}.lean"
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(generate_lean_code(x, y, z, k))
            print(f"  [+] Línea {idx}: Certificado generado en {out_file}")
        else:
            print(f"  [-] Línea {idx}: ({x}, {y}, {z}) no suma {k} (suma={x**3+y**3+z**3}).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
