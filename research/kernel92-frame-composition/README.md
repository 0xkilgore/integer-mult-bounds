# Kernel92 plus delivery-frame optimization

Conditional **kappa = 0.001530327580902932**. This composes PR533's 92-pivot direct504 supplier with PR534's frozen delivery-frame assignment.

| Quantity | PR533 | Composition |
|---|---:|---:|
| Conditional kappa | 0.001524207950793244 | 0.001530327580902932 |
| Complex lower rate | 0.001526534707131015364923 | 0.001532673072778713292743 |
| Local rank mass | 6228 | 6228 |
| Helpers | 504 | 504 |
| Width-8 / width-9 helpers | 164 / 340 | 164 / 340 |
| Live / physical families | 7168 / 7682 | 7168 / 7682 |

The local profile changes to `{1:2174,2:496,3:357,4:226,5:139,6:56,7:8}`. The scalar instructions, kernel selection, helper entrances, cleanup, controller, complete owner assignment and paid idle remainders are retained. Only the frames on the 1,400 delivery-body instructions change.

## Construction and argument

`code/construct.py` reconstructs the pinned PR533 factory and selection, applies the frozen delivery frames, recounts actual frame chains and runs the independently supplied monotone-lift checker. Every new frame contains its constructor frame, and predecessor/successor nesting and fixed center/target barriers are checked. Applying legal lifts from last operation to first gives the coalescing argument inherited from PR531. No search is part of verification.

Changed frames are then independently transported and checked on all arbitrary input columns in both orientations. The actual emitted local program, all local phases and endpoint adapters, residual wrappers, whole-owner program, physical controller, finite invoice, two exact moment engines and all 47 outer inequalities are replayed.

## Verification status at draft publication

Exact provisional pricing, monotone lifts, scalar transport, independent local replay and wrappers passed. Full local phase and downstream owner/invoice replay are running; their receipts will be added after completion. This draft does not claim a completed package replay or green CI.

Run on Python 3.11+ with assertions enabled:

```sh
python -B verify.py /absolute/path/to/new-output
```

The verifier uses the standard library and requires a new output directory outside this package. Pinned unchanged controller/data phases and the PR493 bit operator remain dependencies. All-size compilation, common-label/mutable-basis realization, normalized wrappers, restored rows, precision/tape and analytic transfer remain conditional. This is not an unconditional theorem, full Lean proof, or measured runtime speedup.

## Sources

[PR533](https://github.com/CrocSwap/integer-mult-bounds/pull/533), [PR534](https://github.com/CrocSwap/integer-mult-bounds/pull/534), and the preserved PR531 construction supply the underlying improvements. See NOTICE.md and SOURCES.json for attribution and exact source pins. Historical source documents and receipts describe their own earlier words, not verification of this composition.
