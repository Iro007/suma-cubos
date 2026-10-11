import Mathlib

/-!
# Algebraic foundation of the exact finite divisor search

These theorems certify algebraic facts, not the Python implementation or
absence of solutions for any globally open target. No sorry/native_decide.
-/
namespace SumaCubos

/-- Sum-of-two-cubes factorization supplies the divisor condition. -/
theorem cube_sum_factorization (x y : ℤ) :
    x^3 + y^3 = (x+y)*(x^2-x*y+y^2) := by
  ring

/-- Every integer solution satisfies the signed discriminant identity. -/
theorem signed_discriminant (x y z k : ℤ) (h : x^3+y^3+z^3=k) :
    3*(x+y)*(4*(k-z^3)-(x+y)^3) = (3*(x+y)*(x-y))^2 := by
  rw [← h]
  ring

/-- The signed sum of the first two coordinates divides the remainder. -/
theorem divisor_necessary (x y z k : ℤ) (h : x^3+y^3+z^3=k) :
    (x+y) ∣ (k-z^3) := by
  use x^2-x*y+y^2
  rw [← h]
  ring

/-- Reconstruction with exact parity equations and discriminant is sound. -/
theorem reconstruction_sound (x y s v z k : ℤ)
    (hx : 2*x=s+v) (hy : 2*y=s-v)
    (hv : 3*s*v^2=4*(k-z^3)-s^3) : x^3+y^3+z^3=k := by
  have hs : s=x+y := by omega
  have hvs : v=x-y := by omega
  rw [hs, hvs] at hv
  nlinarith [hv]

/-- Replacing the signed divisor with its absolute value gives a square. -/
theorem unsigned_discriminant (x y z k d : ℤ)
    (h : x^3+y^3+z^3=k) (hd : d=|x+y|) :
    3*d*(4*|k-z^3|-d^3) = (3*d*(x-y))^2 := by
  have hq : 0 ≤ x^2-x*y+y^2 := by
    nlinarith [sq_nonneg (x-y), sq_nonneg (x+y)]
  have hdiff : |k-z^3| = d*(x^2-x*y+y^2) := by
    calc
      |k-z^3| = |x^3+y^3| := by congr 1; linarith [h]
      _ = |(x+y)*(x^2-x*y+y^2)| := by rw [cube_sum_factorization]
      _ = |x+y| * (x^2-x*y+y^2) := by rw [abs_mul, abs_of_nonneg hq]
      _ = d*(x^2-x*y+y^2) := by rw [← hd]
  have hd2 : d^2=(x+y)^2 := by
    rcases le_total 0 (x+y) with hp | hn
    · rw [hd, abs_of_nonneg hp]
    · rw [hd, abs_of_nonpos hn]
      ring
  rw [hdiff]
  calc
    3*d*(4*(d*(x^2-x*y+y^2))-d^3) =
        3*d^2*(4*(x^2-x*y+y^2)-d^2) := by ring
    _ = 3*d^2*(4*(x^2-x*y+y^2)-(x+y)^2) := by rw [hd2]
    _ = (3*d*(x-y))^2 := by ring

/-- Finite search bound: a z bound implies a divisor bound, not an x/y bound. -/
theorem divisor_cube_bound (x y z k d B : ℤ)
    (h : x^3+y^3+z^3=k) (hd : d=|x+y|)
    (hB : 0 ≤ B) (hz : |z| ≤ B) : d^3 ≤ 4*(B^3+|k|) := by
  have hdnonneg : 0 ≤ d := by rw [hd]; exact abs_nonneg _
  have hBcube : 0 ≤ B^3 := pow_nonneg hB 3
  by_cases hd0 : d=0
  · rw [hd0]
    nlinarith [abs_nonneg k]
  have hdpos : 0 < 3*d := by omega
  have hdelta := unsigned_discriminant x y z k d h hd
  have hbracket : 0 ≤ 4*|k-z^3|-d^3 := by
    by_contra hnot
    have hn : 4*|k-z^3|-d^3 < 0 := lt_of_not_ge hnot
    have hp := mul_neg_of_pos_of_neg hdpos hn
    nlinarith [sq_nonneg (3*d*(x-y))]
  have hzpow : |z|^3 ≤ B^3 := pow_le_pow_left₀ (abs_nonneg z) hz 3
  have htriangle : |k-z^3| ≤ |k|+|z|^3 := by
    simpa only [sub_zero, zero_sub, abs_neg, abs_pow] using (abs_sub_le k 0 (z^3))
  linarith

/-- The excluded S=0 branch is possible only for a cube target. -/
theorem zero_sum_branch (x y z k : ℤ)
    (h : x^3+y^3+z^3=k) (hs : x+y=0) : k=z^3 := by
  have hy : y = -x := by omega
  rw [hy] at h
  nlinarith [h]

/-- Known control solution, not a new discovery. -/
theorem control_k3 : (-5 : ℤ)^3+4^3+4^3=3 := by norm_num

theorem control_k75 :
    (-435203231 : ℤ)^3+435203083^3+4381159^3=75 := by norm_num

theorem control_k165 :
    (-385495523231271884 : ℤ)^3+383344975542639445^3+98422560467622814^3=165 := by
  norm_num

theorem control_k579 :
    (143075750505019222645 : ℤ)^3+(-143070303858622169975)^3+(-6941531883806363291)^3=579 := by
  norm_num

theorem control_k906 :
    (-74924259395610397 : ℤ)^3+72054089679353378^3+35961979615356503^3=906 := by
  norm_num

#print axioms divisor_cube_bound
#print axioms reconstruction_sound
#print axioms control_k579
end SumaCubos
