# Lemma A (paid wrappers, spectators, one owner) of PR #484: clean proof and Lean 4 formalisation

Lemma A of #484 (§3) has two parts.
* **Exact part, checked numerically.** `S_E = L_E (C_[w] ⊗ I) R_E` on every entrance frame.
* **Realization part, assumed from #458 §3.** Paid wrappers around a whole invocation of a family, with nothing else acting on that family meanwhile, leave the host with its residual and its spectators untouched.

Others now rely on the realization part:
* #500 uses the paid wrappers;
* #505 (the current frontier) lists "#484 Lemma A realization" among its retained conditions.

This package proves the realization part in Lean 4, in general:
* any semiring, any modules and any charts;
* hosted families, banks and same-owner spectators alike;
* any number of stages.

The hypotheses are exactly the schedule conditions, and each is checked on the real words. `PROOF.md` holds the clean statement and proof. The package is stacked on the Lemma G package `../e8-lemma-g-lean`; it reuses its event semantics as a Lake path dependency.

## Proved in Lean (`LemmaA/`, Lean 4.21.0 + Mathlib v4.21.0, the pin of `formal/lean` on main)

**Main theorem:**

```lean
theorem LemmaA.lemmaA_family (T : Λ → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (σ : Hosting ι Φ K W (A ⊗[K] B))
    (hinj : Function.Injective σ.own) (rec : Λ → Λ → A ⊗[K] B → A ⊗[K] B) (es : List (Event ι Λ K))
    (l : ι → Λ) (y : Φ → W) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (j : ι)
    (hS : ∀ s, S es j s = if s = j then 1 else 0) (C : A →ₗ[K] A)
    (hfac : ∀ v, T (labRun es l j) ((T (l j)).symm v) = C.rTensor B v) :
    realizeRun σ rec es y (σ.own j) = (σ.chart j).symm (C.rTensor B (σ.chart j (y (σ.own j))))
```

In words: suppose the invocation has one owner per unit, is well labelled with exact recipes, gives the helper a unit row, and its helper block factors as `C ⊗ id`. Then at the end of the complete invocation, the helper's family holds `chart⁻¹ (C ⊗ id) chart` of its own initial value. The spectators are untouched.

| theorem | content |
| --- | --- |
| `realize_run`, `realize_untouched` | one owner ⇒ the physical execution, read through the charts, is the local run; unowned families are untouched |
| `one_owner_needed` | without one owner, a one-event stream already breaks this |
| `family_endpoint`, `endpoint_indep` | with Lemma G's unit row and zero column, the helper's family ends as a function of itself, and no other family reads it |
| `spectators_fixed`, `helper_block`, `lemmaA_family` | the wrapped block `C ⊗ id` keeps every spectator factor |
| `commute_of_disjoint`, `shuffle_eval`, `whole_invocation` | an invocation interleaved with actions that touch none of its families equals the whole invocation followed by those actions ("no other actor") |
| `split_off` | the endpoint splits into a piece on the helper's family and a rest that does not touch it |
| `pieces_commute`, `pieces_product` | pieces on disjoint blocks of one pending child commute, and multiply to `C ⊗ D` |
| `async_window`, `defer`, `gather` | **#505's variant**: a borrowed piece moves to the pending child's deadline past every commuting action, and the gathered pieces give the child |

No instance data is enumerated in Lean, and no `decide`/`native_decide` is used. `#print axioms` gives a subset of `[propext, Classical.choice, Quot.sound]` for every theorem above (`PrintAxioms.lean`).

## Checked on the words (PROOF.md §4)

| hypothesis | check |
| --- | --- |
| (F) exact factorization | #484 `adapters_gk.py` on the 16 entrance frames, and I-helper on 122/122 entering helpers, 512 columns each |
| (E) exact endpoint, unit helper rows | the Lemma G package: H1–H3 |
| (O) one owner | #484 `audit_hosted_gk.py --one-helper-per-family`, plus the **new** `code/check_owners.py`, which checks literal injectivity on the emitted template |
| (W) whole invocation, windows | #484 `audit_hosted_gk.py`: atomic calls, windows re-derived from the schedule |
| charts, blocks | #484 `audit_hosted_gk.py`: host and bank charts, disjoint slots |

`check_owners.py` results:

| word | calls injective on whole families | the other calls |
| --- | --- | --- |
| headline | 72/72 | — |
| gauge80 | 40/72 | injective with #433's pure-bank slots as units |
| kernel79 | 56/72 | injective with #433's pure-bank slots as units |

In every call of every word, each entering (wrapped) helper is the only register on its family.

## #505

Each invocation of #505 is whole and has distinct helper owners that are not active data. It therefore meets Lemma A as stated. Borrowing another replica's pending block inside that child's open window is Variant A′ (`async_window`). Its hypotheses are #505's scheduling conditions:
* per-replica order;
* window;
* disjoint, covering blocks;
* whole invocations;
* the deadline.

#505's own replay checks them; this package does not re-run it.

## Trust base

* The Lean kernel (4.21.0), Mathlib v4.21.0 (rev `308445d`), and the axioms `propext`, `Classical.choice`, `Quot.sound`.
* The Lemma G package, which is built here from source.
* #484's numerical checks of (F), and its hosting audit.
* `code/check_owners.py`.
* Inherited interfaces:
  * #442's compiler, under which the local program acts identically on the batch coordinates;
  * #433's pure-bank slot interface, for width-9 helpers in gauge80 and kernel79 only.

## Run

```sh
python3 research/e8-lemma-a-lean/verify.py                                    # Lean: manifest, source scan, cache get, build, axioms
python3 research/e8-lemma-a-lean/verify.py --instances /abs/out/of/484/verify # plus #484's recorded results and check_owners.py
```

* `lake build` also builds `../e8-lemma-g-lean`, the Lemma G package.
* `--instances` needs the output directory of #484's `verify.py`. That run takes about 25 minutes; with `--all` it also covers gauge80 and kernel79.

## Credits

* The one-helper rule, paid wrappers and spectator routing: #458 (chafreaky).
* The complete-invocation normalisation and same-owner spectator borrowing: #471 (Dugongue).
* Asynchronous whole-owner replicas: #505 (Dugongue).
* The conjugation lemma and event semantics: #425 (Zhihao Chen).
* The gauge/kernel word and Lemma A: #484 (DreamingOfClouds).
* Lean conventions: the `formal/lean` pin on main; #487/#488 (jamesyc).
