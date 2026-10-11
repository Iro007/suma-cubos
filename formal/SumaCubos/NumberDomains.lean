import Mathlib

/-! Positive rational denominator bounds and an exact Gaussian witness.
The Gaussian nonexistence search below height 23 remains computational.
-/
namespace SumaCubosDomains

/-- Positivity bounds each numerator when the common denominator is at most 5. -/
theorem numerator_bound (a : ℕ) (h : a^3 ≤ 14250) : a ≤ 24 := by
  by_contra hn
  have h25 : 25 ≤ a := by omega
  have hpow : (25 : ℕ)^3 ≤ a^3 := pow_le_pow_left₀ (Nat.zero_le 25) h25 3
  norm_num at hpow
  omega

/-- A finite, kernel-evaluated check over all numerator and denominator values. -/
set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem small_denominator_check :
    ∀ (q : Fin 6) (a b c : Fin 25),
      (0 < q.val ∧ 0 < a.val ∧ 0 < b.val ∧ 0 < c.val) →
      a.val^3+b.val^3+c.val^3 ≠ 114*q.val^3 := by
  decide

/-- No strictly positive rational representation with a common denominator below 6. -/
theorem no_positive_denominator_below_six (q a b c : ℕ)
    (hq : 0 < q) (hq6 : q < 6) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    a^3+b^3+c^3 ≠ 114*q^3 := by
  intro heq
  have hq5 : q ≤ 5 := by omega
  have hqpow : q^3 ≤ 125 := by
    calc
      q^3 ≤ (5 : ℕ)^3 := pow_le_pow_left₀ (Nat.zero_le q) hq5 3
      _ = 125 := by norm_num
  have haBound : a ≤ 24 := numerator_bound a (by omega)
  have hbBound : b ≤ 24 := numerator_bound b (by omega)
  have hcBound : c ≤ 24 := numerator_bound c (by omega)
  exact small_denominator_check ⟨q,hq6⟩ ⟨a,by omega⟩ ⟨b,by omega⟩ ⟨c,by omega⟩
    ⟨hq,ha,hb,hc⟩ heq

/-- An admissible common denominator is defined through positive integer numerators. -/
def PositiveCommonDenominator (q : ℕ) : Prop :=
    0 < q ∧ ∃ a b c : ℕ, 0 < a ∧ 0 < b ∧ 0 < c ∧ a^3+b^3+c^3=114*q^3

/-- Exact minimum, for three strictly positive rational coordinates. -/
theorem minimum_positive_common_denominator :
    PositiveCommonDenominator 6 ∧
      ∀ q : ℕ, PositiveCommonDenominator q → 6 ≤ q := by
  constructor
  · refine ⟨by norm_num, 13,14,27, ?_⟩
    norm_num
  · intro q hq
    rcases hq with ⟨hqpos,a,b,c,ha,hb,hc,heq⟩
    by_contra hn
    exact no_positive_denominator_below_six q a b c hqpos (by omega) ha hb hc heq

/-- Clearing a positive common denominator relates fractions to the integer equation. -/
theorem rational_numerators_equiv (a b c q : ℕ) (hq : q ≠ 0) :
    ((a : ℚ)/q)^3+((b : ℚ)/q)^3+((c : ℚ)/q)^3=114 ↔
      a^3+b^3+c^3=114*q^3 := by
  have hqcast : (q : ℚ) ≠ 0 := by exact_mod_cast hq
  have hfrac : ((a : ℚ)/q)^3+((b : ℚ)/q)^3+((c : ℚ)/q)^3 =
      ((a : ℚ)^3+(b : ℚ)^3+(c : ℚ)^3)/(q : ℚ)^3 := by
    field_simp [hqcast]
    <;> ring
  rw [hfrac, div_eq_iff (pow_ne_zero 3 hqcast)]
  norm_cast

/-- The concrete rational witness is positive in all three coordinates. -/
theorem positive_rational_k114 :
    ((13 : ℚ)/6)^3+((7 : ℚ)/3)^3+((9 : ℚ)/2)^3=114 ∧
      0 < (13 : ℚ)/6 ∧ 0 < (7 : ℚ)/3 ∧ 0 < (9 : ℚ)/2 := by
  norm_num

/-- Exact Gaussian-integer witness, embedded into the complex numbers. -/
theorem gaussian_k114 :
    ((-23 : ℂ)-10*Complex.I)^3+
      ((-23 : ℂ)+10*Complex.I)^3+(22 : ℂ)^3=114 := by
  apply Complex.ext <;> norm_num [pow_succ, Complex.mul_re, Complex.mul_im]

def gaussianHeight (a b c d e f : ℤ) : ℤ :=
    max (max |a| |b|) (max (max |c| |d|) (max |e| |f|))

/-- Component height of the witness. This theorem does not prove minimality. -/
theorem gaussian_witness_height : gaussianHeight (-23) (-10) (-23) 10 22 0 = 23 := by
  norm_num [gaussianHeight]

#print axioms minimum_positive_common_denominator
#print axioms rational_numerators_equiv
#print axioms gaussian_k114
end SumaCubosDomains
