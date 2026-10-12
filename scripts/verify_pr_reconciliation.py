#!/usr/bin/env python3
"""Check immutable snapshot, subsequent family rounds and incorporation receipts.

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
    family_path = ROOT / 'research/community-family533-audit/DISPOSITIONS.json'
    if family_path.exists():
        family = json.loads(family_path.read_text())
        numbers = [p['number'] for p in family['pull_requests']]
        require(len(numbers) == len(set(numbers)), 'Duplicate family PR')
        for row in family['pull_requests']:
            if row['number'] not in expected:
                expected[row['number']] = row['metadata']
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
    receipt_path = ROOT / 'docs/research/community-formal-20261012-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for path, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Changed batch receipt: {path}')
        source = json.loads((ROOT / 'research/community-formal-20261012-audit/SOURCE.json').read_text())
        for path, digest in source['source_files'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Changed reviewed source: {path}')
        for number, head in receipt['reviewed_heads'].items():
            require(actual[int(number)]['starting_head'] == head, f'#{number}: batch head mismatch')
        print('PASS formal/tooling batch: reviewed heads, source inventory and execution receipt bindings')
    receipt_path = ROOT / 'docs/research/community-family533-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for path, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                    f'Changed construction-family receipt: {path}')
        source = json.loads((ROOT / 'research/community-family533-audit/SOURCE.json').read_text())
        for path, digest in source['source_files'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                    f'Changed construction-family source: {path}')
        for number, head in receipt['reviewed_heads'].items():
            require(actual[int(number)]['current_head'] == head, f'#{number}: family head mismatch')
        closures = ROOT / 'research/community-family533-audit/CLOSURES.json'
        if closures.exists():
            for row in json.loads(closures.read_text())['closures']:
                item = actual[row['number']]
                require(item['disposition'] == 'incorporated' and item['github_state'] == row['github_state'],
                        'Closure does not match disposition')
                require(row['reviewed_head'] == item['current_head'] and row['comment_url'],
                        'Closure lacks head or explanation')
        print('PASS construction/formal family: complete source inventory, replay evidence and supported closures')
    print(f'PASS immutable snapshot plus explicit family rounds: {len(actual)} PRs, attributed heads, evidence pins and unresolved questions')


if __name__ == '__main__':
    main()
