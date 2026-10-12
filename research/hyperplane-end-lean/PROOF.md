# Hyperplane-ended helpers: Lemma A with an arbitrary terminal frame

A dirty entering helper may end at a hyperplane frame `U` (dim 8) instead of `FULL` (dim 9): its single cleanup gate
`h -= p` runs right after part B, in a `cleanup_tail` phase, at the join `U` of the frames of `h` and its partner `p`.
This package proves in Lean 4 that Lemma A's realization still applies. The wrapped residual of such a helper is exactly
`C ⊗ id`, global phase included, whenever the exact factorization `T_U T_E⁻¹ = L (C ⊗ id) R` holds for its pair
`(E, U)`. For the 38 helpers of the c8 words, `C = C_[7]` with `7 = |U| − |E|`.

The package reuses Lemma A's and Lemma G's definitions (`Event`, `physRun`, `labRun`, `WellLabelled`, `RecipesExact`,
`S`, `Hosting`, `realizeRun`, `streamOwner`, `Frame`) through Lake path dependencies. It restates none of them. Lean
names are in brackets.

## 1. Why a generalization is enough

Lemma A (`../e8-lemma-a-lean/PROOF.md` §2) is stated for an arbitrary label family `T : Λ → M ≃ M`. Its hypothesis (F)
is `T_{λ¹_j} T_{λ⁰_j}⁻¹ = C ⊗ id` on Lemma G's extended labels `λ⁰_j = (prew, j)`, `λ¹_j = (done, j)`. `FULL` occurs
only in how Lemma G's PROOF.md §1.3 defines the operator of `(done, j)`: `T_(done,j) = L_E⁻¹ T_FULL`. So the work is to:

1. define the extended labels with an arbitrary terminal frame `U_j`, and wrappers keyed by the pair `(E_j, U_j)`;
2. show that the wrappers then execute exactly `R_{E,U}⁻¹` and `L_{E,U}⁻¹`, so the HPE word is still an instance of
   Lemma G's event model with exact recipes;
3. derive (F) from the exact factorization (N), and show that the HPE word's labels are well formed;
4. apply Lemma A unchanged.

## 2. Definitions (`HyperplaneEnd/Labels.lean`)

* **Extended labels** [`XLab ι Fr`]: `frame F`, `prew j` or `done j`.
* **Their operators** [`Text T ent term Lw Rw`], for the word's frame family `T`, entrance frames `ent j`, terminal
  frames `term j` and wrapper monomials `Lw E U`, `Rw E U`:
  * `T_(frame F) = T_F`;
  * `T_(prew,j) = R_{E_j,U_j} T_{E_j}`;
  * `T_(done,j) = L_{E_j,U_j}⁻¹ T_{U_j}`.

  With `term j = FULL` and `Lw E FULL = L_E`, `Rw E FULL = R_E`, this is Lemma G's §1.3 definition verbatim. So the
  FULL-ended helpers of #484 are the instance `term j = ⊤`.

## 3. Statements and proofs

**Wrapper recipes** [`pre_recipe`, `post_recipe`]. The pre wrapper `relabel j (prew j) (E_j)` executes
`T_E T_(prew,j)⁻¹ = R_{E,U}⁻¹`. The post wrapper `relabel j (U_j) (done j)` executes `T_(done,j) T_U⁻¹ = L_{E,U}⁻¹`.
*Proof:* unfold `Text` and cancel.

**Wrapped block** [`wrapped_block`]. `T_(done,j) T_(prew,j)⁻¹ = L⁻¹ T_U T_E⁻¹ R⁻¹`.

**(N) ⇒ (F)** [`factor_of_exact`]. If `T_U T_E⁻¹ = L (C ⊗ id) R` holds exactly for `(E_j, U_j)`, then
`T_(done,j) T_(prew,j)⁻¹ = C ⊗ id`. *Proof:* rewrite with `wrapped_block` and (N); `L⁻¹ L` and `R R⁻¹` cancel. The
equality is between linear maps, so no phase is dropped.

**The pre wrapper must be the `(E, U)` recipe** [`factor_iff_pre`]. Let (N) hold with `L, R` and an invertible `C`.
Suppose the pre wrapper that ran executed `R'⁻¹`. Then `L⁻¹ T_U T_E⁻¹ R'⁻¹ = C ⊗ id` if and only if `R' = R`.
*Proof:* the left side is `(C ⊗ id) R R'⁻¹`, and `C ⊗ id` is injective (`LinearEquiv.rTensor`). This is the formal
content of the review's finding F1: a pre wrapper decoded against `R_{E,FULL}` instead of `R_{E,U}` breaks (F).

**The `cleanup_tail` segment** [`tail`, `tail_labels`] (`HyperplaneEnd/Tail.lean`). The tail
`[relabel h A_h U, relabel p A_p U, add h p q]` is well labelled: the gate runs with both operands at `U`, which is G0.
It leaves `h` and `p` at `U` and every other register's label unchanged.

**The HPE word's labels** [`hpe_labels`]. Take the word `a ++ tail ++ b ++ [relabel h U (done h)]`, where:
* `a` is well labelled and brings `h` to `A_h` and `p` to `A_p`, with `h ≠ p`;
* `b` (the rest of the cleanup, at FULL) is well labelled and never relabels `h`.

Then the whole word is well labelled, and `h` ends at `(done, h)`. *Proof:* `labRun_untouched` (Lemma G) keeps `h` at `U`
through `b`, so the post wrapper is admissible. Composition is `wellLabelled_append` and `labRun_append`.

**(C) for a hyperplane end** [`residual_block`]. In frame labels without wrappers, a helper with a unit row running
from `E` to `U` ends as `T_U T_E⁻¹` of its own input, for any frame `U`. *Proof:* Lemma G's `row_unit`.

**Main theorems** (`HyperplaneEnd/Main.lean`). Assume the following:
* exact recipes in the labels `Text`;
* the invocation is well labelled;
* the helper `j` has a unit row (Lemma G H3), starts at `(prew, j)` and ends at `(done, j)`;
* (N) holds for the pair `(ent j, term j)`, with any terminal frame `term j`.

Then the following hold.
* [`hpe_block`] The register ends as `(C ⊗ id) h_j`.
* [`hpe_family`] Under one owner per family, the helper's family ends as `χ⁻¹ (C ⊗ id) χ` of its own initial value.
* [`hpe_streams`] The same holds on the physical streams `(fam r, d·σ_r⁻¹)` when registers that share a family have
  disjoint nonempty footprints. This is `LemmaA.lemmaA_streams` with (F) discharged.
* [`hpe_word`] The same holds for the concrete word of `hpe_labels`, with `U = term h`. Its label hypotheses are those of
  `hpe_labels`, so the start/end tags need not be assumed separately.

*Proof:* apply `LemmaA.helper_block`, `lemmaA_family` and `lemmaA_streams` with `T := Text …`, and supply (F) from
`factor_of_exact` after rewriting the start and end labels.

Lemma A's other conclusions are stated for an arbitrary label family. So they hold for the labels `Text` without change:
* no other reader (`endpoint_indep`, which needs the helper's zero column);
* single-unit piece (`lemmaA_piece`);
* split-off and asynchronous borrowing (`split_off`, `lemmaA_async`);
* pieces on disjoint blocks commute and gather (`pieces_commute`, `pieces_product`).

**Width on frames** [`hyperplane_width`]. Let `E ≤ U` be frames of `F₂⁹` with `dim E = 1` and `dim U = 8`. Then the
residual width is `dim U − dim E = 7`, the hosted chart has `9 − 7 = 2` spectators, and `U ≠ FULL` (`dim ⊤ = 9`).

## 4. What is not proved in Lean, and where it is checked

The theorems take the following as hypotheses. They are checked on the emitted words by the HPE tools
(`scratch/HostingShapeScout/hpe/`, reviewed in `HyperplaneReviewer/FINAL-REPORT.md`), not in Lean.

| hypothesis | meaning | checked by |
| --- | --- | --- |
| (N) `hN` | `T_U T_E⁻¹ = L_{E,U} (C_[7] ⊗ I) R_{E,U}` exactly, global phase included, for every `(E, U)` pair of the word | `hpe/code/adapters_local.py` (recipes keyed `"E:U"`), wrapper check "L^-1 S_E R^-1 = C_[w] x I for 39 entrance frames, global phase included", 10 wrapper mutations rejected (`runs/v2/L_ck38.wrap.log`); review: 38/38 helpers, a width-8 claim rejected |
| `hrec` | every climb executes `T_B T_A⁻¹`; the wrappers execute `R_{E,U}⁻¹`, `L_{E,U}⁻¹` (by `pre_recipe`/`post_recipe`, exactly when the emitted wrapper is the `"E:U"` recipe) | independent emitted replay forward and backward; the 5th wrapper field `U` (review F1 fix); controls `hpe_pre_wrapper_resolved_to_full_recipe` etc. |
| `hw`, tail shape, `hmv` | G0 in `cleanup_tail`; no later gate relabels `h` | `audit_local.py` (`cur[r] == f` for both operands; `cur[h] = U ≠ FULL`), `audit_and_transport.py` assert, controls `hpe_tail_gate_at_full_frame`, `hpe_tail_gate_moved_into_full_cleanup` |
| `hS` | unit helper row (and zero column for `endpoint_indep`) | exact forward and inverse-transpose replay on all 728 columns (`audit_and_transport.py`) |
| (O′), (W) | disjoint footprints; whole invocations | unchanged from Lemma A (`../e8-lemma-a-lean/code/`) |

**No instance enumeration in Lean.** Like the Lemma A and Lemma G packages, this package uses no `decide` or
`native_decide`. The exact factorization over `ℂ^{2⁹}` for each `(E, U)` pair is a numerical-exact check in the HPE
tools. Lean proves that this hypothesis, together with the label discipline above, implies the realized endpoint
`χ⁻¹ (C_[7] ⊗ I₂) χ`.

**Instance check** (`code/check_hpe_pairs.py`, standard library, independent of the HPE tools). For every gate of the
word's `tail` it checks the following over `F₂⁹`, using the word's frame bases:
* the hypotheses of `hyperplane_width`: `dim E = 1`, `dim U = 8`, `E ≤ U` and `U ≠ FULL`;
* the shape used by `tail`/`hpe_labels`:
  * the gate is `h -= p` with `h ≠ p`, and each helper has exactly one tail gate;
  * `final[h] = U`, so the post wrapper names `U`;
  * no gate of the remaining cleanup touches `h`;
* that (N) was checked exactly for the pair: `WRAPPER-CHECKS.json` passes, and lists `(E, U)` with width `dim U − dim E`.

Six mutants must be rejected, and are: `U = FULL`; the gate `h += p`; a post wrapper naming FULL; the gate left in the
FULL cleanup; a pair missing from the exact check; width 8 reported. Results on the HPE local runs
(`hpe/runs/v2/L_*`):

| word | HPE helpers | distinct `(E, U)` pairs (helpers each) | result |
| --- | --- | --- | --- |
| ck (`L_ck38`) | 38 | 3 (24, 8, 6) | PASS, 6/6 mutants rejected |
| atm3 (`L_atm338`) | 38 | 3 (24, 8, 6) | PASS, 6/6 mutants rejected |
| jp8 (`L_jp838`) | 38 | 3 (24, 8, 6) | PASS, 6/6 mutants rejected |

`python3 verify.py --instances RUN_DIR ...` runs it after the Lean checks.

## 5. Trust base

* Lean 4.21.0, Mathlib v4.21.0 (rev `308445d`), and the axioms `propext`, `Classical.choice`, `Quot.sound`. All 13
  named results depend on a subset of these (`PrintAxioms.lean`).
* The Lemma A and Lemma G packages, built here from source.
* The HPE tools' exact checks of the hypotheses in §4.

## 6. Run

```sh
python3 research/hyperplane-end-lean/verify.py                       # source scan, cache get, lake build, axioms
python3 research/hyperplane-end-lean/verify.py --instances RUN_DIR…  # plus code/check_hpe_pairs.py on HPE local runs
```

`lake build` also builds `../e8-lemma-a-lean` and `../e8-lemma-g-lean` (Lake path dependencies, same Lean and Mathlib
pin).
