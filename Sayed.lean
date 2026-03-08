/-
# قانون السيد (The Sayed Law)
برهان آلي باستخدام Lean
-/

import data.nat.prime
import tactic.linarith

theorem sayed_law (p q : ℕ) (hp : nat.prime p) (hq : nat.prime q)
  (hp2 : nat.prime (p+2)) (hq2 : nat.prime (q+2))
  (h : p * (p+2) = q * (q+2)) : p = q :=
begin
  -- (p-q)*(p+q+2) = 0
  have h1 : (p - q) * (p + q + 2) = 0,
  { calc (p - q) * (p + q + 2)
        = (p - q) * (p + q) + (p - q) * 2 : by ring
    ... = (p^2 - q^2) + 2*p - 2*q         : by ring
    ... = (p^2 + 2*p) - (q^2 + 2*q)       : by ring
    ... = p * (p+2) - q * (q+2)           : by ring
    ... = 0                               : by rw h },

  -- p + q + 2 > 0
  have h2 : p + q + 2 > 0 := by linarith [nat.prime.pos hp, nat.prime.pos hq],

  -- استنتاج p = q
  exact eq_of_mul_eq_zero_right h2 h1,
end
