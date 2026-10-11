# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Instance check A-own (PROOF.md §4): the owner map of every invocation is injective on owner units.

`LemmaA.realize_run` needs `Function.Injective own` over every register of the invocation.  #484's hosting audit
(`audit_hosted_gk.py --one-helper-per-family`) enforces one owner per data family and per entering helper's bank family,
and admits #433's pure width-9 banks, in which several width-9 helpers of one invocation share a bank family in disjoint
9-cell slots (no wrapper acts on them).  This script checks, on the emitted hosted template, in every call:
  * units: the owner units are pairwise distinct, where a unit is a family, or a (family, slot) of a pure width-9 bank
    (#433's slot interface);
  * every entering (wrapped) helper is the ONLY register on its family: its spectators lie in that family outside its slot;
  * no owner lies in the private namespace.
It also counts the calls whose owner map is injective on whole families (no slot interface needed).  It also reports the route kinds
(1 data wire, 3 hosted width-9, 4 hosted entering with spectator record, [2, off, w, spectators] banked entering,
[2, slot] pure-bank width-9) and checks the template against #484's EXPECTED.json.

usage: check_owners.py BASE VARIANT [VARIANT ...]     (BASE = the output directory of #484's verify.py)
Standard library only; reads BASE/<variant>/hosted/GLOBAL-TEMPLATE.json.gz."""
import gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = json.loads((HERE.parents[1] / 'e8-complex-gauge-kernel' / 'EXPECTED.json').read_text())


def kind(r):
    return str(r[0]) if r[0] != 2 else ('2-slot' if len(r) == 2 else '2-entering')


def check(base, name):
    raw = (base / name / 'hosted' / 'GLOBAL-TEMPLATE.json.gz').read_bytes()
    t = json.loads(gzip.decompress(raw)); live = t['live']; bad = []; kinds = Counter(); calls = 0; literal = 0
    for c in t['calls']:
        own = c['owners']; calls += 1; tag = f"call stage {c['stage']} replica {c['replica']}"
        fams = [f for f, _ in own]; cnt = Counter(fams)
        units = [(f, r[1]) if kind(r) == '2-slot' else f for f, r in own]
        literal += len(set(fams)) == len(fams)
        if len(set(units)) != len(units): bad.append(f'{tag}: owner units not distinct')
        for f, r in own:
            if kind(r) in ('4', '2-entering') and cnt[f] != 1: bad.append(f'{tag}: entering helper shares family {f}')
            if kind(r) == '2-slot' and any(kind(r2) != '2-slot' for f2, r2 in own if f2 == f): bad.append(f'{tag}: pure bank {f} mixed')
        if any(f >= live for f in fams): bad.append(f'{tag}: owner in the private namespace')
        kinds.update(kind(r) for _, r in own)
    exp = EXPECTED['words'].get(name, {}).get('hosted_template_sha256')
    got = hashlib.sha256(raw).hexdigest(), hashlib.sha256(gzip.decompress(raw)).hexdigest()
    pinned = exp is None or exp in got
    if not pinned: bad.append('hosted template differs from #484 EXPECTED.json')
    return calls, literal, dict(sorted(kinds.items())), bad, exp is not None


def main():
    base, ok = Path(sys.argv[1]), True
    for name in sys.argv[2:]:
        calls, literal, kinds, bad, pinned = check(base, name)
        ok &= not bad
        print(name, 'calls', calls, 'injective on whole families', literal, 'route kinds', kinds, 'pinned to EXPECTED' if pinned else 'no EXPECTED pin',
              'violations', len(bad), bad[:3], flush=True)
    print('PASS owner units injective, entering helpers sole owners' if ok else 'FAIL owner maps')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
