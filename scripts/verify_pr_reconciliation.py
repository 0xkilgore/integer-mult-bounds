#!/usr/bin/env python3
"""Check fixed-snapshot coverage and exact archived-source incorporation receipts.

Offline integrity check, not a mathematical verifier or a live GitHub-state check.
"""
from pathlib import Path
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/pr-reconciliation-20261012'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
    snapshot = json.loads((AUDIT / 'starting-snapshot.json').read_text())
    expected = {p['number']: p for p in snapshot['pull_requests']}
    actual = {p['number']: p for p in ledger['pull_requests']}
    require(len(actual) == len(ledger['pull_requests']) == len(expected), 'Duplicate or missing PR')
    require(actual.keys() == expected.keys(), 'Starting PR set changed')
    for number, pr in actual.items():
        require(pr['starting_head'] == expected[number]['headRefOid'], f'#{number}: starting head changed')
        require(pr['contributor'] == expected[number]['author'], f'#{number}: attribution changed')
        require(pr['disposition'] in {'unreviewed', 'partially_reviewed', 'changed_since_review',
                                     'incorporated', 'superseded'}, f'#{number}: unknown disposition')
        if pr['disposition'] not in ('incorporated', 'superseded'):
            require(bool(pr['unresolved_question']), f'#{number}: missing remaining question')
    for path, digest in ledger['source_sha256'].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Stale source: {path}')
    package = ROOT / 'research/coordinated-frames-and-entrance-banks'
    manifest = json.loads((package / 'BASELINE.json').read_text())
    parts = []
    for item in manifest['parts']:
        data = (package / item['file']).read_bytes()
        require(len(data) == item['bytes'], 'Archive part size')
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Archive part digest')
        parts.append(data)
    data = b''.join(parts)
    require(hashlib.sha256(data).hexdigest() == manifest['archive_sha256'], 'Archive digest')
    archive = {}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            body = z.read(name)
            archive[name] = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    require(len(archive) == manifest['files'], 'Archive file count')
    checks = json.loads((AUDIT / 'incorporation-checks.json').read_text())['checks']
    comparison = json.loads((AUDIT / 'content-comparison.json').read_text())
    for number, check in checks.items():
        files = json.loads((AUDIT / f'pr{number}-files.json').read_text())
        head = json.loads((AUDIT / f'pr{number}-head.json').read_text())
        require(check['head'] == head['headRefOid'] == actual[int(number)]['starting_head'], 'Head mismatch')
        require(len(files) == len({f['filename'] for f in files}) == check['changed_files'] == head['changedFiles'], 'Incomplete changed-file list')
        require(not comparison[number]['unresolved'], 'Unresolved paths in closure candidate')
        for f in files:
            require(f['status'] in ('added', 'modified'), 'Deletion/rename requires separate semantic review')
            require(archive.get(f['filename']) == f['sha'], f'#{number}: absent/different archive file {f["filename"]}')
        print(f'PASS #{number}: all {len(files)} changed files match the published historical archive')
    print(f'PASS fixed snapshot: {len(actual)} PRs, attributed heads, evidence pins and unresolved questions')


if __name__ == '__main__':
    main()
