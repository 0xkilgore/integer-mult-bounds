/-
Lemma A, spectators: the wrapped helper block is `C ⊗ id`, so the spectator factor is untouched,
and pieces on complementary tensor factors of one family commute and multiply to `C ⊗ D`.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
-/
import LemmaA.Schedule
import Mathlib.LinearAlgebra.TensorProduct.Basic

namespace LemmaA

open TensorProduct LemmaG LemmaG.Stream

variable {K : Type*} [CommSemiring K]
variable {A B : Type*} [AddCommMonoid A] [Module K A] [AddCommMonoid B] [Module K B]

/-- **Spectators are untouched.**  If the wrapped helper block is `C ⊗ id` (Lemma A, exact part:
`L_E⁻¹ S_E R_E⁻¹ = C_[w] ⊗ I`), each pure tensor keeps its spectator factor. -/
theorem spectators_fixed (G : A ⊗[K] B →ₗ[K] A ⊗[K] B) (C : A →ₗ[K] A)
    (h : G = C.rTensor B) (a : A) (b : B) : G (a ⊗ₜ b) = C a ⊗ₜ b := by
  rw [h]; rfl

/-- Residuals on complementary tensor factors commute. -/
theorem residuals_commute (C : A →ₗ[K] A) (D : B →ₗ[K] B) :
    C.rTensor B ∘ₗ D.lTensor A = D.lTensor A ∘ₗ C.rTensor B := by
  rw [LinearMap.rTensor_comp_lTensor, LinearMap.lTensor_comp_rTensor]

section Helper

variable {ι Λ : Type*} [DecidableEq ι] [Fintype ι]

/-- **The helper block of a complete invocation fixes the spectators.**  Lemma G's unit row gives
the block `T_{λ¹ j} T_{λ⁰ j}⁻¹`; with the exact factorization of that block as `C ⊗ id` (checked
numerically), register `j` ends as `(C ⊗ id) h_j`. -/
theorem helper_block (T : Λ → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (rec : Λ → Λ → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι Λ K)) (l : ι → Λ) (h : ι → A ⊗[K] B) (hrec : RecipesExact T rec es)
    (hw : WellLabelled es l) (j : ι) (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (C : A →ₗ[K] A) (hfac : ∀ v, T (labRun es l j) ((T (l j)).symm v) = C.rTensor B v) :
    physRun rec es h j = C.rTensor B (h j) := by
  rw [row_unit T rec es l h hrec hw j hS, hfac]

/-- **Lemma A, realized helper family.**  One owner per invocation, exact recipes, well labelled,
a unit row (Lemma G, H3) and the exact factorization `T_{λ¹}T_{λ⁰}⁻¹ = C ⊗ id`: at the end of the
complete invocation the helper's family holds `χ⁻¹ (C ⊗ id) χ` of its own initial value.  With
`endpoint_indep` no other family reads it, and with `whole_invocation` no other actor may run on
it meanwhile. -/
theorem lemmaA_family {Φ W : Type*} [DecidableEq Φ] [AddCommMonoid W] [Module K W]
    (T : Λ → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (σ : Hosting ι Φ K W (A ⊗[K] B))
    (hinj : Function.Injective σ.own) (rec : Λ → Λ → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι Λ K)) (l : ι → Λ) (y : Φ → W) (hrec : RecipesExact T rec es)
    (hw : WellLabelled es l) (j : ι) (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (C : A →ₗ[K] A) (hfac : ∀ v, T (labRun es l j) ((T (l j)).symm v) = C.rTensor B v) :
    realizeRun σ rec es y (σ.own j) = (σ.chart j).symm (C.rTensor B (σ.chart j (y (σ.own j)))) := by
  rw [family_endpoint T σ hinj rec es l y hrec hw j hS, hfac]

end Helper

section Family

variable {Φ W : Type*} [DecidableEq Φ] [AddCommMonoid W] [Module K W]

/-- Apply `U` to family `f` and leave every other family alone. -/
def famAct (f : Φ) (U : W → W) : (Φ → W) → (Φ → W) :=
  fun y => Function.update y f (U (y f))

omit [AddCommMonoid W] in
theorem famAct_supported (f : Φ) (U : W → W) : Supported (famAct f U) {f} := by
  refine ⟨fun y g hg => Function.update_of_ne (by simpa using hg) _ _, fun y y' hyy g hg => ?_⟩
  rw [Set.mem_singleton_iff.1 hg]
  simp [famAct, hyy f rfl]

omit [AddCommMonoid W] in
theorem famAct_comp (f : Φ) (U V : W → W) : famAct f U ∘ famAct f V = famAct f (U ∘ V) := by
  funext y g
  by_cases hg : g = f
  · subst hg; simp [famAct]
  · simp [famAct, Function.update_of_ne hg]

/-- **Pieces on disjoint blocks of one family commute.**  In a common chart `χ : W ≃ A ⊗ B`, one
piece acts as `C ⊗ id` and the other as `id ⊗ D`. -/
theorem pieces_commute (χ : W ≃ₗ[K] A ⊗[K] B) (f : Φ) (C : A →ₗ[K] A) (D : B →ₗ[K] B) :
    famAct f (χ.symm ∘ C.rTensor B ∘ χ) ∘ famAct f (χ.symm ∘ D.lTensor A ∘ χ) =
      famAct f (χ.symm ∘ D.lTensor A ∘ χ) ∘ famAct f (χ.symm ∘ C.rTensor B ∘ χ) := by
  have key : (χ.symm ∘ C.rTensor B ∘ χ) ∘ (χ.symm ∘ D.lTensor A ∘ χ) =
      (χ.symm ∘ D.lTensor A ∘ χ) ∘ (χ.symm ∘ C.rTensor B ∘ χ) := by
    funext v
    have := LinearMap.congr_fun (residuals_commute C D) (χ v)
    simp only [LinearMap.comp_apply] at this
    simp [this]
  rw [famAct_comp, famAct_comp, key]

/-- **Pieces gather into the child.**  The two pieces together act as `χ⁻¹ (C ⊗ D) χ`. -/
theorem pieces_product (χ : W ≃ₗ[K] A ⊗[K] B) (f : Φ) (C : A →ₗ[K] A) (D : B →ₗ[K] B) :
    evalW [famAct f (χ.symm ∘ C.rTensor B ∘ χ), famAct f (χ.symm ∘ D.lTensor A ∘ χ)] =
      famAct f (χ.symm ∘ TensorProduct.map C D ∘ χ) := by
  have key : (χ.symm ∘ D.lTensor A ∘ χ) ∘ (χ.symm ∘ C.rTensor B ∘ χ) =
      χ.symm ∘ TensorProduct.map C D ∘ χ := by
    funext v
    have := LinearMap.congr_fun (LinearMap.lTensor_comp_rTensor (f := C) (g := D)) (χ v)
    simp only [LinearMap.comp_apply] at this
    simp [this]
  simp only [evalW]
  rw [Function.id_comp, famAct_comp, key]

end Family

end LemmaA
