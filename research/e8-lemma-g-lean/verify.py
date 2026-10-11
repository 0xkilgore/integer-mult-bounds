# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Verify the Lean formalisation of Lemma G.

usage: python3 verify.py [--no-cache] [--instances BASE]
  1. every file listed in MANIFEST.json has its recorded sha256 and no unlisted file sits in LemmaG/ or code/;
  2. the Lean sources contain no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern`, `unsafe`, `opaque`
     and no `set_option` other than the heartbeat limits;
  3. `lake exe cache get` (Mathlib's pinned build, skipped with --no-cache) and `lake build`, warnings shown;
  4. `lake env lean PrintAxioms.lean`: each main theorem depends only on propext, Classical.choice, Quot.sound;
  5. with --instances BASE (BASE = the output directory of PR #484's verify.py, with or without --all):
     code/check_extended_labels.py on every word present (headline and anchor required; --all adds gauge80 and kernel79).
Python 3.9+, standard library only; `lake` from elan on PATH (the toolchain is pinned by lean-toolchain)."""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = re.compile(r'\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b|set_option\s+(?!maxHeartbeats|maxRecDepth)')


def fail(msg):
    print('FAIL', msg, flush=True); sys.exit(1)


def run(cmd, timeout):
    print('$', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    if p.returncode:
        print(p.stdout[-4000:]); fail(f'{cmd[0]} {cmd[1]} exited {p.returncode}')
    return p.stdout


def strip_comments(src):
    src = re.sub(r'/-.*?-/', ' ', src, flags=re.S)          # block and doc comments (not nested in these sources)
    return re.sub(r'--[^\n]*', ' ', src)


def main():
    args = sys.argv[1:]
    man = json.loads((HERE / 'MANIFEST.json').read_text())
    for rel, sha in man['files'].items():
        got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        if got != sha: fail(f'sha256 of {rel}')
    for d in ('LemmaG', 'code'):
        for p in (HERE / d).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and str(p.relative_to(HERE)) not in man['files']:
                fail(f'unlisted file {p.relative_to(HERE)}')
    print('manifest: %d files OK' % len(man['files']), flush=True)

    lean_files = sorted(HERE.glob('LemmaG/*.lean')) + [HERE / 'LemmaG.lean', HERE / 'PrintAxioms.lean']
    for p in lean_files:
        m = FORBIDDEN.search(strip_comments(p.read_text()))
        if m: fail(f'forbidden token {m.group(0)!r} in {p.name}')
    print('sources: no sorry / admit / axiom / native_decide / unsafe / opaque / extern in %d files' % len(lean_files), flush=True)

    if '--no-cache' not in args:
        run(['lake', 'exe', 'cache', 'get'], 3600)
    out = run(['lake', 'build'], 3600)
    print('\n'.join(l for l in out.splitlines() if 'warning' in l or 'error' in l or 'Build completed' in l), flush=True)

    out = run(['lake', 'env', 'lean', 'PrintAxioms.lean'], 1200)
    wanted = [l.split()[2] for l in (HERE / 'PrintAxioms.lean').read_text().splitlines() if l.startswith('#print axioms')]
    seen = {}
    for m in re.finditer(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", out):
        seen[m.group(1)] = [a.strip() for a in m.group(2).split(',') if a.strip()]
    for m in re.finditer(r"'([\w.']+)' does not depend on any axioms", out):
        seen[m.group(1)] = []
    print(out.strip(), flush=True)
    for name in wanted:
        if name not in seen: fail(f'no axiom report for {name}')
        if not set(seen[name]) <= ALLOWED: fail(f'{name} depends on {seen[name]}')
    print('axioms: %d theorems, only %s' % (len(wanted), sorted(ALLOWED)), flush=True)

    if '--instances' in args:
        base = Path(args[args.index('--instances') + 1])
        words = [w for w in ('gauge80-kernel42', 'gauge80', 'kernel79', 'anchor') if (base / w / 'split-centres').is_dir()]
        if not {'gauge80-kernel42', 'anchor'} <= set(words): fail(f'{base} lacks the headline word or the anchor')
        run([sys.executable, '-B', 'code/check_extended_labels.py', str(base), *words, '--mutants'], 3600)
        print('instances: extended-label check PASS on', ', '.join(words), flush=True)
    print('PASS Lemma G Lean verification', flush=True)


if __name__ == '__main__':
    main()
