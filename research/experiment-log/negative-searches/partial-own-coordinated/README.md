# Coordinated gauges on the partial-own factory

Source: PR507 at 8d4444cf8a16d500cbb94add6e4fa8bcfb9c7d5e, with PR508 four-gauge mechanism at 3213fc136270ca8372ce9f8fbb828e78ba96cecf. Helpers 540 through 543 change together. The earlier partial-own-async category preserves the exact bare-core reconstruction and candidate words.

The changed word passed fresh scalar/frame, Gaussian, wrapper, readback, labels, word mutations, guarded helper instances, guarded whole-program simulation and retimed Lemma G mutations. These checks reuse the completed partial-own factory and unchanged provider; they do not admit a new global allocation.

The aggregate fixed-order LP showed a floating cost gain of 50.13743185065687. A 60-second MILP returned a feasible integer incumbent with gain 43.48133549303748, gap 0.00006630626651159228 and floating b 0.0013900120172621463. It reached the time limit; no optimality claim is made.

**This incumbent failed the stricter pattern-to-call flow feasibility check.** The fixed pattern counts cannot be assigned under the per-pattern distinct-call constraints. No repaired.json was emitted. The subsequent realization launcher incorrectly proceeded and failed with FileNotFoundError; this is an orchestration failure, not a second mathematical counterexample. Both logs are retained. The empty output directory contains no owners or plan. Do not use the floating root as an admitted bound.

The next search incorporates pattern-to-call constraints jointly with pattern selection; its script is retained, but this snapshot makes no claim about its unfinished solve. The published verified PR473 value remains conditional kappa 0.001388049083313897.

Scripts retain original frontier390 discovery paths. Full source and licenses are preserved in PR473 complex-partial-own-async; these are historical experiment records, not standalone verification entrypoints. Credit eumemic for the new factory, Dugongue for coordinated gauges and asynchronous scheduling, retained earlier authors, and Rohan Arun with OpenAI Codex assistance for this composition attempt.
