#!/usr/bin/env python3
"""Audit PR628's instruction word with abstract, exact leaf operations.

Standard library only. The producer's arithmetic, factor preparation, solvers,
and rounding routines are not imported. See README.md for the precise scope.
Prepared for @0xkilgore with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(word):
    return [(f, x, y, -s) for f, x, y, s in reversed(word)]


def reference_word(factors, x=0, y=1, depth=0):
    """Compile the mathematical bracket, independent of compose's dispatcher."""
    if len(factors) == 1:
        return [(factors[0], x, y, 1)]
    split = len(factors) // 2
    z = depth + 2
    right = reference_word(factors[:split], x, z, depth + 1)
    left = reference_word(factors[split:], z, y, depth + 1)
    return right + left + inverse(right) + inverse(left)


def producer_function(source):
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == 'compose']
    need(len(functions) == 1, 'one pinned compose definition required')
    # Only the public compose function is executed. All leaf calls are replaced
    # by abstract operations; unrelated producer top-level code never executes.
    namespace = {'c': SimpleNamespace(need=need, norm2=lambda t: abs(t) ** 2)}
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, 'pinned-pr628-compose', 'exec'), namespace)
    return namespace


def producer_word(namespace, n, sign=1, alias=None, shortage=False):
    arrays = [[0] for _ in range(2 + (n - 1).bit_length())]
    if alias is not None:
        dst, src = alias
        arrays[dst] = arrays[src]
    scratch = arrays[2:]
    if shortage:
        scratch = scratch[:-1]
    labels = {id(a): i for i, a in enumerate(arrays)}
    word = []

    def capture(x, y, factor, phases, beta, bits, direction, s, stats):
        word.append((factor, labels[id(x)], labels[id(y)], s))

    namespace['leaf'] = capture
    namespace['compose'](arrays[0], arrays[1], list(range(n)), scratch,
                         [1], 1, 1, 1, sign)
    return word


def add(left, right, sign=1):
    result = Counter(dict(left))
    for atom, coefficient in right:
        result[atom] += sign * coefficient
    # Counter's + operator discards negative coefficients: do not use it here.
    return tuple(sorted((atom, value) for atom, value in result.items() if value))


class FreeTerms:
    """Free abelian expressions with uninterpreted unary function atoms.

    Equal arguments to the same function have equal atoms. No additivity,
    continuity, approximation, or zero-preservation of a leaf is assumed.
    Hash-consing keeps shared expression DAGs compact.
    """
    def __init__(self, registers):
        self.atoms = {}
        self.dependencies = []
        self.initial = [self.atom(('input', i), {i}) for i in range(registers)]

    def atom(self, key, dependencies):
        if key not in self.atoms:
            self.atoms[key] = len(self.dependencies)
            self.dependencies.append(frozenset(dependencies))
        return ((self.atoms[key], 1),)

    def depends(self, expression):
        return frozenset().union(*(self.dependencies[i] for i, _ in expression))

    def apply(self, factor, expression):
        return self.atom(('function', factor, expression), self.depends(expression))

    def run(self, word, state=None):
        state = list(self.initial if state is None else state)
        for factor, src, dst, sign in word:
            need(src != dst, 'abstract leaf aliases source and target')
            state[dst] = add(state[dst], self.apply(factor, state[src]), sign)
        return state


def run_linear(word, registers):
    """Free noncommuting linear maps: monomials are (input, operator word)."""
    state = [(((i, ()), 1),) for i in range(registers)]
    initial = state[:]
    for factor, src, dst, sign in word:
        mapped = tuple(((var, (factor,) + operators), coefficient)
                       for (var, operators), coefficient in state[src])
        state[dst] = add(state[dst], mapped, sign)
    return initial, state


@lru_cache(None)
def recurrence(n):
    return 1 if n == 1 else 2 * (recurrence(n // 2) + recurrence(n - n // 2))


def closed_count(n):
    q = 1 << (n.bit_length() - 1)
    return 3 * q * n - 2 * q * q


def restoration_ok(word, n, inverse_word=None):
    registers = 2 + (n - 1).bit_length()
    engine = FreeTerms(registers)
    state = engine.run(word)
    initial = engine.initial
    need(all(state[i] == initial[i] for i in range(registers) if i != 1),
         'source or scratch not restored')
    increment = add(state[1], initial[1], -1)
    need(1 not in engine.depends(increment), 'increment depends on target')
    need(engine.run(inverse(word) if inverse_word is None else inverse_word,
                    state) == initial, 'whole word is not inverted')
    linear_initial, linear_state = run_linear(word, registers)
    expected = linear_initial[:]
    expected[1] = add(expected[1], (((0, tuple(reversed(range(n)))), 1),))
    need(linear_state == expected, 'wrong linear product or uncancelled dirt')
    return len(engine.atoms), len(engine.depends(increment) - {0})


def must_fail(name, function):
    try:
        function()
    except ValueError as error:
        return {'name': name, 'detected': str(error)}
    raise ValueError('negative control survived: ' + name)


def collect():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    for path, expected in manifest['vendored_sha256'].items():
        need(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == expected,
             'source hash mismatch: ' + path)
    source = (HERE / 'vendor/pr628_dirty.py').read_text()
    namespace = producer_function(source)
    cases = []
    for n in range(1, 65):
        reference = reference_word(list(range(n)))
        positive = producer_word(namespace, n)
        negative = producer_word(namespace, n, -1)
        need(positive == reference, 'producer/reference positive word mismatch')
        need(negative == inverse(reference), 'producer/reference inverse mismatch')
        need(len(reference) == closed_count(n), 'instruction count mismatch')
        atoms, dirty_dependencies = restoration_ok(positive, n, negative)
        cases.append({'factors': n, 'leaf_calls': len(reference),
                      'scratch_arrays': (n - 1).bit_length(),
                      'free_term_atoms': atoms,
                      'possible_dirty_dependencies': dirty_dependencies})

    for n in range(1, 10001):
        q = 1 << (n.bit_length() - 1)
        count = recurrence(n)
        need(count == closed_count(n), 'recurrence/closed count mismatch')
        need(9 * n * n - 8 * count == (3 * n - 4 * q) ** 2,
             'sharp envelope identity mismatch')

    # Instruction mutations are applied to the pinned routine, then checked by
    # the abstract oracle. Each replacement must match exactly once.
    mutations = [
        ('inverse_without_reversal', 'in reversed(operations)', 'in operations'),
        ('omit_final_A_inverse', '(x,z,B,-1),(z,y,A,-1)', '(x,z,B,-1)'),
        ('omit_B_restoration', '(x,z,B,-1),(z,y,A,-1)', '(z,y,A,-1)'),
    ]
    controls = []
    for name, old, new in mutations:
        need(source.count(old) == 1, 'ambiguous mutation: ' + name)
        mutant = producer_function(source.replace(old, new))
        controls.append(must_fail(name, lambda m=mutant:
            restoration_ok(producer_word(m, 3), 3, producer_word(m, 3, -1))))
    for name, alias in [('borrow_ancestor_target', (2, 1)),
                        ('borrow_ancestor_source', (2, 0)),
                        ('reuse_scratch_depth', (3, 2))]:
        controls.append(must_fail(name, lambda a=alias:
            producer_word(namespace, 3, alias=a)))
    controls.append(must_fail('missing_scratch_depth', lambda:
                              producer_word(namespace, 3, shortage=True)))

    # Concrete nonlinear example: B(t)=t and A(t)=t^2 over the integers.
    # Restoration holds, but an increment need not be independent of scratch.
    nonlinear = []
    for dirt in (0, 1):
        state = [1, 7, dirt]
        for f, src, dst, sign in reference_word([0, 1]):
            state[dst] += sign * (state[src] if f == 0 else state[src] ** 2)
        need(state[0] == 1 and state[2] == dirt, 'nonlinear restoration')
        nonlinear.append({'initial_scratch': dirt, 'target_increment': state[1] - 7})
    need(nonlinear[0]['target_increment'] != nonlinear[1]['target_increment'],
         'scratch-independence negative control did not distinguish dirt')

    return {'status': 'PASS', 'base_commit': manifest['base_commit'],
            'subject_head': manifest['subject']['commit'], 'assignment_seed': 62,
            'symbolic_factor_counts': [1, 64], 'symbolic_cases': cases,
            'recurrence_factor_counts': [1, 10000],
            'negative_controls': controls, 'nonlinear_scratch_counterexample': nonlinear,
            'scope': 'Exact finite symbolic instruction audit, with a separate written '
                     'all-n proof; no leaf accuracy, bit-cost, or multiplication proof.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a fresh JSON certificate')
    parser.add_argument('--check', action='store_true', help='compare with EXPECTED.json')
    args = parser.parse_args()
    result = collect()
    payload = json.dumps(result, indent=2) + '\n'
    if args.check:
        need(result == json.loads((HERE / 'EXPECTED.json').read_text()),
             'committed certificate mismatch')
    if args.write:
        args.write.write_text(payload)
    print('PASS: 64 symbolic words; 10000 recurrence cases; 7 rejected controls; '
          'nonlinear dirt counterexample. n=62: 3904 leaves, 6 scratch arrays.')


if __name__ == '__main__':
    main()
