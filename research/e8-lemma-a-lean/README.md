# Lemma A (paid wrappers, spectators, one owner) of PR #484: clean proof and Lean 4 formalisation

Lemma A of #484 (§3) has two parts:
* **exact part:** `S_E = L_E (C_[w] ⊗ I) R_E` on every entrance frame. #484 checks this numerically.
* **realization part:** paid wrappers around a whole invocation, with nothing else acting meanwhile, leave the host with its residual and its spectators untouched. #484 assumed this from #458 §3.

This package proves the realization part in Lean 4 and checks every hypothesis on the emitted words. `PROOF.md` holds the clean statement and proof. The package is stacked on the Lemma G package `../e8-lemma-g-lean`, whose event semantics it reuses through a Lake path dependency.

**Model.** Units are physical streams `(family F, cover class g ∈ O(73,2))`, as in the cover model that #484 inherits from #442 and #458. At cover class `d`, register `r` lives on the stream `(F_r, d·σ_r⁻¹)`, where `σ_r` is its route. One owner per stream follows when registers that share a family have pairwise disjoint footprints. So the theorem covers:
* one helper per family (#458, #484);
* #433's pure-bank slots and #442's hosted slots;
* #471's and #500's footprint rule.

**Coverage on #484's words.** Every call of all four words satisfies the hypotheses:
* the headline: 72/72 calls with one register per family;
* gauge80: 40 such calls, plus 32 slot-sharing calls;
* kernel79: 56 such calls, plus 16 slot-sharing calls;
* the anchor: 72 hosted-slot calls, all sharing a family.

## Proved in Lean (`LemmaA/`, Lean 4.21.0 + Mathlib v4.21.0, the pin of `formal/lean` on main)

**Main theorem, on streams.** It holds over any commutative semiring, for any modules, charts and number of stages.

```lean
theorem LemmaA.lemmaA_streams (T : Λ → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set C) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[K] (A ⊗[K] B)) (rec : Λ → Λ → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι Λ K)) (l : ι → Λ) (y : Fam × G → W) (hrec : RecipesExact T rec es)
    (hw : WellLabelled es l) (j : ι) (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (Cj : A →ₗ[K] A) (hfac : ∀ v, T (labRun es l j) ((T (l j)).symm v) = Cj.rTensor B v) :
    realizeRun ⟨streamOwner fam σ d, chart⟩ rec es y (streamOwner fam σ d j) =
      (chart j).symm (Cj.rTensor B (chart j (y (streamOwner fam σ d j))))
```

In words, the theorem assumes:
* registers that share a family have pairwise disjoint footprints;
* the invocation is well labelled with exact recipes;
* the helper has a unit row (Lemma G);
* its block factors as `C ⊗ id`, in Lemma G's extended labels (where `T_{λ¹}T_{λ⁰}⁻¹ = L_E⁻¹ S_E R_E⁻¹`).

Then after the complete invocation, the helper's stream holds `chart⁻¹ (C ⊗ id) chart` of its own initial value. The spectators are untouched.

| theorem | content |
| --- | --- |
| `streamOwner_injective(_of_disjoint)`, `sweep_unique` | distinct routes, or disjoint footprints, give distinct streams; the cover sweep visits each stream once per route |
| `realize_run`, `realize_untouched`, `one_owner_needed` | with one owner per unit, the physical execution read through the charts is the local run; within the model, sharing a unit breaks this |
| `family_endpoint`, `endpoint_indep`, `lemmaA_family`, `lemmaA_piece` | the helper's unit ends as a function of itself, no other unit reads it, and the invocation acts on it as a single-unit piece |
| `spectators_fixed`, `helper_block` | the wrapped block `C ⊗ id` keeps every spectator factor |
| `commute_of_disjoint`, `shuffle_eval`, `whole_invocation` | no other actor: interleaving with actions that avoid the invocation's units is harmless |
| `split_off`, `pieces_commute`, `pieces_product` | pieces on disjoint blocks of one pending child commute and multiply to `C ⊗ D` |
| `lemmaA_async`, `async_window`, `defer`, `gather` | Variant A′ (#505): a borrowed piece moves to its child's deadline past every commuting action, and the gathered pieces give the child |

There is no instance enumeration and no `decide`/`native_decide`. `#print axioms` gives a subset of `[propext, Classical.choice, Quot.sound]` for all 23 theorems (`PrintAxioms.lean`).

## Checked on the words (PROOF.md §4)

| hypothesis | check | headline / gauge80 / kernel79 / anchor |
| --- | --- | --- |
| (F) in extended labels | #484 `adapters_gk.py` and I-helper; Lemma G `check_extended_labels.py` | 16 frames, 122 / 80 / 79 helpers; anchor has no wrappers; 0 tag violations |
| (E) | Lemma G package H1–H3 | 0 violations |
| (O′) one owner per stream, centre copies | **new** `code/check_owners.py` (3 mutants) | 0 violations on all four words |
| (W), windows, disjoint blocks | **new** `code/check_windows.py` (independent; 2 mutants); `loop_order`; #484 hosting audit | 39,792 / 38,112 / 37,720 / 34,560 blocks; 0 violations |

## #505 and #512

**#505.** Its invocations are whole. Per #505's own text, "all 800 families per invocation are distinct", so (O) holds literally. Its cross-replica borrowing is Variant A′. Variant A′ needs three conditions:
* windows;
* disjoint blocks;
* whole invocations with distinct owners.

`verify.py --async T.json.gz` runs `check_owners.py` and `check_windows.py` on an asynchronous template. Results on the template that #505's own `verify.py` emits:
* #505's `verify.py` passes every stage here, including its independent audit. Its final template-hash comparison with #505's `EXPECTED.json` fails, although the owner, sigma-stream, profile and κ records match its shipped evidence.
* `check_owners.py`: one register per family in 72/72 calls.
* `check_windows.py`: all 40,320 hosted blocks lie inside their owner child's open window, with blocks disjoint and family-group windows disjoint.
* The Variant A′ hypotheses therefore hold on #505's schedule.

#505's other conditions are not re-checked here: per-replica order, the prefix bound and its invoice.

**#512.** Its layout reports 800 distinct physical owners per invocation, and it builds on #505's asynchronous machinery. It is covered on that report and under the same conditions. #512's word is not checked here.

## Trust base

* The Lean kernel (4.21.0), Mathlib v4.21.0 (rev `308445d`), and the axioms `propext`, `Classical.choice`, `Quot.sound`.
* The Lemma G package, built here from source.
* #484's numerical checks of (F), and its hosting audit.
* This package's instance checks: `code/check_owners.py`, `code/check_windows.py`, and Lemma G's `check_extended_labels.py`.
* Inherited interfaces:
  * #442's cover model, in which streams `(F, g)` are the physical units;
  * #442's compiler, under which the local program acts identically on the batch coordinates.

## Run

```sh
python3 research/e8-lemma-a-lean/verify.py                                    # Lean: manifest, source scan, cache get, build, axioms
python3 research/e8-lemma-a-lean/verify.py --instances /abs/out/of/484/verify # plus #484's results, extended labels, owners, windows
python3 research/e8-lemma-a-lean/verify.py --no-cache --async T.json.gz       # owners and windows on an asynchronous template
```

* `lake build` also builds `../e8-lemma-g-lean`.
* `--instances` needs the output directory of #484's `verify.py`; run it with `--all` to include gauge80 and kernel79.

## Credits

* #458 (chafreaky): the one-helper rule, paid wrappers, spectator routing, cover-class owners, and the realization argument formalised here.
* #471 (Dugongue): complete-invocation normalisation, same-owner spectator borrowing, and the footprint rule.
* #500 (rohanarun): footprint hosting with paid wrappers.
* #505 (Dugongue): asynchronous whole-owner replicas.
* #433 (icekylinx): the complex supplier and its pure banks.
* #442 (DaysSky): whole-residual and idle-axis hosting, and the stream model.
* #425 (Zhihao Chen): the conjugation lemma.
* #484 (DreamingOfClouds): the gauge/kernel word and Lemma A.
* Lean conventions: the `formal/lean` pin on main; #487/#488 (jamesyc).
