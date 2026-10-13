# Validation receipt

Executed locally on macOS with Python 3.14.7 (Clang 17.0.0), 2026-10-12
America/Chicago. These are local results; no remote Linux or CI pass is asserted.

| Check | Result |
| --- | --- |
| `python3 -B research/dirty-commutator-audit/verify.py --check` | PASS |
| Same command with `-O` | PASS; explicit checks remain active |
| Standalone copy outside repository, `python3 -I -B /path/to/copy/verify.py --check` | PASS; no repository or external-package imports |
| Append a comment to copied vendored source, rerun under `-I -O -B` | Exit 1, `source hash mismatch` |
| Restore source, change copied `EXPECTED.json` status, rerun under `-I -O -B` | Exit 1, `committed certificate mismatch` |
| `python3 -B scripts/verify_selected_result.py` | PASS, unchanged selected κ `51110230636731/31250000000000000` |

The public command checks all 64 symbolic factor counts, all 10,000 recurrence
cases, seven instruction/interface rejection controls, and the concrete nonlinear
scratch example. See README.md for mathematical scope and exact expected output.

A separate Codex reviewer independently derived the proofs, reviewed the complete
new package, compared the vendored files with the fetched pinned originals, and
ran the public command. No blocking findings were reported. This is substantial
AI-assisted review, not a human peer review or a formal theorem certification.

No selected supplier, generator, `upstream/` file, or existing artifact changed.
The repository-wide regenerating `make verify` and selected supplier cold replay
were not run for this standalone audit. Their status is not inferred from the
targeted checks above.
