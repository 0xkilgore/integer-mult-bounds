# Sprint claim: balanced dirty commutator audit

- Track: adversarial mathematical audit; OS-random assignment seed **62**.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Subject: PR #628, head `0768f97d06c623b8211e651543c66135796b62bf`,
  `research/prime-power-cyclic-scan/DIRTY-PROOF.md` and `dirty.py`.
- Precise obligation: exact restoration and inverse-word order of the balanced
  dirty-scratch commutator under nonlinear rounded leaves, including uneven
  splits, and its complete leaf-call recurrence.
- Method: independent symbolic/abstract leaf execution, exact recurrence,
  targeted instruction and alias controls; compare with the pinned implementation.
  Seed 62 selects candidate 3 (`62 mod 3 = 2`) and the uneven split at 62 leaves.
- Expected deliverable: scoped audit note, executable exact evidence and source
  pins. No new supplier or multiplication exponent claim.
- Claimed 2026-10-12 22:06 America/Chicago; expected finish by 22:51.

Three narrow candidates considered: (1) prime-ideal/resultant exclusion in
accepted #621; (2) Fourier-series to cyclic-operator transfer in #621;
(3) nonlinear dirty restoration and leaf-call accounting in pending #628.
The first two already have an incorporated written review and two arithmetic
engines. Candidate 3 permits an abstract symbolic method distinct from #628's
dense rational numerical-accuracy comparisons.

Coordination: GitHub's pinned-issue query returned no pinned issues. Open PR
metadata through #660 and the central review ledger were inspected. #628 is
the direct predecessor; #647 concerns a different exact-RAM construction.
No other rounded cyclic dirty-commutator audit was identified in that snapshot.
This local claim is used as requested instead of opening a reservation issue.

Contributor: @0xkilgore, with substantial OpenAI Codex assistance. Apache-2.0.

## Completion update

Completed the [scoped audit and exact call-count proof](README.md), with the
[reproducible certificate](EXPECTED.json) and [validation receipt](VALIDATION.md).
No restoration defect was found under the stated primitive contract. The exact
leaf count is `3*q*n - 2*q*q`, `q=2^floor(log2(n))`, with sharp supremum
`9*n*n/8`; this replaces the conservative `4*n*n` execution allowance without
changing the asymptotic order or claiming a new κ. At `n=62`, all 3904 leaves
are accounted for. Nonlinear, noncommuting and rejection checks passed.

Before submission, open-PR metadata was refreshed through #662. PR628's head
remained `0768f97d06c623b8211e651543c66135796b62bf`; it had no review comments.
No overlapping symbolic dirty-commutator audit appeared among the 100 most
recently updated open PRs, and the refreshed pinned-issue list remained empty.
This is independent evidence for part of PR628, not a replacement for its
rounded-leaf accuracy checks or a review of its full theorem.
