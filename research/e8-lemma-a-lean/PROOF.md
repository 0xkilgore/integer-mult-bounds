# Lemma A: clean statement and proof

Lemma A of PR #484 (`research/e8-complex-gauge-kernel/PROOF.md` §3) has two parts.

* **Exact part (checked numerically by #484).** For every entrance frame,
  `S_E = L_E (C_[w] ⊗ I) R_E`, with `L_E`, `R_E` Gaussian monomials. The wrapped product of every entering
  helper's emitted chain is `C_[w] ⊗ I`.
* **Realization part (assumed from #458 §3).** The wrappers surround a whole invocation, and nothing else acts on
  the helper's family during it. Then the host is left with its assigned residual and identical spectators. This
  must hold for hosted families and banks alike, and at nine stages.

This package proves the realization part as an abstract theorem. The Lean proof covers every chart, every family
layout and every number of stages. The hypotheses are exactly what a schedule must meet: one owner, a whole
invocation, no other actor, and the exact endpoint. Lean names are in brackets. The Lemma G objects (`Event`,
`physRun`, `S`, `WellLabelled`, `RecipesExact`) are reused from `../e8-lemma-g-lean`.

## 1. Setting

* **Owner units.** A global state is `y : Φ → W`, one vector per owner unit. A unit is a physical family. Under
  #433's slot interface, a 9-cell slot of a pure width-9 bank is also a unit (§4).
* **An invocation.** A local stream `es` acts on registers `ι`, as in Lemma G. A **hosting** `σ` gives each register
  `i` an owner `own i ∈ Φ` and a linear chart `chart i : W ≃ M`. The chart is the route (a permutation of an
  orthonormal basis) together with the batch of remaining coordinates.
* **Physical execution** [`realize`, `realizeRun`]. Each event reads its operands through their charts. It writes
  the destination register's unit back through that register's chart.
* **Actions and words** [`Supported`, `evalW`, `Interleave`]. An action on global states is *supported on* `S` if:
  * it changes only units in `S`;
  * its values on `S` depend only on the input on `S`.

  A physical schedule is a word of actions, applied left to right.

## 2. Statement

**Lemma A (realization).** Let `σ` host the invocation `es`, and let `j` be an entering helper. Assume the following.

* **(O) One owner.** `own` is injective on the registers of the invocation.
* **(W) Whole invocation, no other actor.** The physical word interleaves the realized events of `es` with other
  actions. Each other action is supported on a set that contains no unit of the invocation.
* **(E) Exact endpoint (Lemma G).** `es` is well labelled with exact recipes. Row `j` of its scalar shadow is `e_j`,
  and column `j` vanishes off the diagonal.
* **(F) Exact factorization (#484, exact part).** In the chart `M = A ⊗ B` (residual ⊗ spectators and batch),
  `T_{λ¹_j} T_{λ⁰_j}⁻¹ = C ⊗ id`.

Then:

1. The word equals the complete invocation followed by the other actions [`whole_invocation`]. Read through the
   charts, the invocation is the local run [`realize_run`]. Units that host no register are untouched
   [`realize_untouched`].
2. The helper's unit ends as `chart_j⁻¹ (C ⊗ id) chart_j` applied to its own initial value [`lemmaA_family`,
   `family_endpoint`]. On a pure tensor `a ⊗ b`, it gives `C a ⊗ b`: **the spectators are untouched**
   [`spectators_fixed`, `helper_block`].
3. No other unit's final value depends on the helper's unit [`endpoint_indep`]. The endpoint therefore splits into
   a piece supported on `{own j}` and a rest that neither reads nor writes `own j` [`split_off`].
4. *Pending blocks.* Two pieces of one pending child, on disjoint blocks of a common chart, commute
   [`pieces_commute`]. Together they act as `C ⊗ D` [`pieces_product`]. A family's pending child is
   `⊗_b C_b` over its pending axes. So its residual blocks and the paid remainder multiply back to the child: "the
   original idle operator is recovered" (#458).

**(O) is necessary** [`one_owner_needed`]. If two registers share a unit, the one-event stream `scale i 0` changes
what register `j` sees, while the local run leaves `j` alone.

**(W) is necessary.** An action that reads the helper's unit between `R_E⁻¹` and `L_E⁻¹` sees `R_E⁻¹h` rather
than `h`. Because `L_E R_E ≠ 1` in general, the wrapped intermediate state is not the host's value.

**Variant A′ (asynchronous borrowing, #505)** [`async_window`, `defer`, `gather`]. Suppose an invocation endpoint
`E` acts on the owner unit `f` as a piece `P`, and nothing else reads `f` (items 2–3). Suppose also that every action
between the invocation and the pending child's deadline commutes with `P`. This holds when the action does not touch
`f` [`commute_of_not_mem`], or is another piece of the same child on a disjoint block [`pieces_commute`]. Then the
word equals the one in which the rest of `E` runs in place and `P` runs just before the deadline. Once all pieces of
the child are deferred, they multiply to the child [`gather`, `pieces_product`]. The owner's history is then the
original one.

## 3. Proofs

* **`realize_run`.** Induct over the stream. Realizing an event writes the destination's unit and leaves every
  other unit alone. Under (O), every other register sits on a different unit, so its view is unchanged; the
  destination's view is its new local value. Hence `view ∘ realize e = e.phys ∘ view`.
* **`family_endpoint`, `lemmaA_family`.**
  * The unit's value is `chart⁻¹(view)`, and the view is the local run.
  * Lemma G's `row_unit` gives `T_{λ¹}T_{λ⁰}⁻¹` applied to the helper's own initial view.
  * (F) rewrites this as `C ⊗ id`, i.e. `rTensor`.
* **`endpoint_indep`.**
  * Changing the helper's unit changes the view only at `j`.
  * By `conj_matrix`, output `r` is `T(Σ_s S_rs T⁻¹ h_s)`, and `S_rj = 0`.
  * Units that host no register are untouched.
* **`commute_of_disjoint`.** Check family by family.
  * On `S`, `B` acts as the identity, so `A` sees the same input.
  * On `T`, the same holds with `A` and `B` exchanged.
  * Elsewhere both act as the identity.
* **`shuffle_eval`.** Induct over the interleaving. A right step moves `b` past all of `as`, using
  `evalW_comm`.
* **`whole_invocation`.** Realized events are supported on `range own` [`realize_supported`]. So they commute with
  the other actions by (W).
* **`split_off`.**
  * At `f`, the piece sees `y f` and returns `E y f`.
  * Elsewhere the rest returns `E y g`. It does not read `f`, by item 3.
* **`async_window`.** Combine `split_off`, then `defer` (an induction with `evalW_comm`).
* **`pieces_commute`, `pieces_product`.** Mathlib's `rTensor_comp_lTensor` and `lTensor_comp_rTensor`: both
  orders compose to `map C D`.

## 4. Instance hypotheses

| | hypothesis | check | result |
| --- | --- | --- | --- |
| (F) | `L_E⁻¹ S_E R_E⁻¹ = C_[w] ⊗ I` for every entrance frame, and the wrapped chain of every entering helper | #484 `adapters_gk.py` (`LEMMA-A.json`, 16 frames, 5 wrapper mutants rejected); #484 `lg_instances` I-helper (all 512 columns) | exact, 122/122 helpers on the headline |
| (E) | well labelled, exact recipes, unit helper rows and zero helper columns | Lemma G package H1–H3 (#484 G0/G2/G3, I-tr, scalar replay; extended labels) | 0 violations |
| (O) | owner units injective per invocation; every entering helper the sole register on its family | #484 `audit_hosted_gk.py --one-helper-per-family` (one owner per data family and per entering bank family); **new** `code/check_owners.py` (literal injectivity on the emitted template) | 0 violations |
| (W) | whole invocation: calls are atomic units of the global template; a hosted helper's call lies strictly inside its idle child's window | #484 `audit_hosted_gk.py` (windows re-derived from the schedule; windows of one family group disjoint) | PASS |
| charts | route = permutation of an orthonormal basis; residual = assigned pending vectors, spectators = first unused indices (host) or first pad cells (bank) | #484 `audit_hosted_gk.py` (host and bank charts, footprints) | PASS |
| blocks | the hosted blocks of one idle child are disjoint, and the remainder is the rest of the child | #484 `audit_hosted_gk.py` (slots disjoint; remainder ranks) | PASS |

**The new check.** `code/check_owners.py` re-reads the emitted hosted template and checks hypothesis (O) literally.

| word | calls injective on whole families | units for the other calls |
| --- | --- | --- |
| headline (gauge80 + kernel42) | 72/72 | none needed |
| gauge80 | 40/72 | pure-bank slots |
| kernel79 | 56/72 | pure-bank slots |

* In the remaining calls of gauge80 and kernel79, some width-9 helpers share a pure bank in disjoint 9-cell slots.
  This is #433's interface. It is admitted, and no wrapper acts on those helpers. With slots as units, the owner map
  is injective in every call.
* In every call of every word, each entering (wrapped) helper is the only register on its family. This is required,
  because its spectators lie in that family outside its slot.
* The anchor is hosted under #442's slot rule, with several width-9 helpers per data family. It has no wrappers and
  is outside Lemma A.

## 5. Scope, and #505

* **#458, #471, #484.** Their arguments are instances of items 1–4.
  * The chart is arbitrary: host chart, bank chart, or #471's "inactive ninth axis of the same owner array".
  * Nothing depends on the number of stages.
  * #458's 11-stage word and #484's nine-stage word therefore both satisfy Lemma A, given their checked (O), (W),
    (E) and (F).
* **#505 (asynchronous whole owners).** Every invocation stays whole and indivisible. Its helper owners are distinct,
  and none is an active data family. So each invocation meets (O), (W), (E) and (F) unchanged.
* **What #505 adds.** A residual block may land on a pending child of *another* replica, at any time inside that
  child's open window: after the owner's previous data or bridge touch, before its next touch. This is **Variant
  A′**, proved above. Its hypotheses are #505's scheduling conditions:
  * per-replica order;
  * owner in its window;
  * blocks disjoint and covering;
  * whole invocations with distinct owners;
  * completion before the deadline.

  They are checked by #505's own replay (`ASYNC-OWNERS.json.gz`), which is not re-run here. The intermediate dirty
  states that pass between replicas affect the prefix bound, which #505 re-invoices. They do not affect exactness.

## 6. Changes relative to #484 §3

1. **The realization part is proved, not assumed.** It holds for every chart and every layout. Hosted families,
   banks and #471's same-owner spectators are all instances.
2. **The one-owner rule is exactly injectivity of the owner map on owner units.** It is necessary
   (`one_owner_needed`).
3. **"Nothing else acts" is exactly** that the interleaved actions avoid the invocation's units (`whole_invocation`).
4. **The spectator claim follows from Lemma G's block structure (H3) and the exact factorization.** No separate
   assumption is needed.
5. **The owner hypothesis is now checked literally.** The headline word needs no slot interface. gauge80 and kernel79
   use #433's pure-bank slots for some width-9 helpers only.
