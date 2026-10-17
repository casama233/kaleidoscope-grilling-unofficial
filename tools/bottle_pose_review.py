"""Reverse only the exact reviewed G105 position delta for historical gates.

Every byte of both preimage and candidate is pinned. Historical full-frustum,
asset and motion assertions remain independent from the new native grip gate.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'tools/fixtures/g105-bottle-pose-reviewed-delta.json'
REVIEW_BASE = 'b8bb78b523fbb17c5dc12e674026f084231b4a7d'


def reviewed_before(path, actual=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    relative = path.relative_to(ROOT).as_posix()
    ledger = json.loads(LEDGER.read_text())
    assert ledger['schema'] == 1 and ledger['release'] == [2, 8, 105]
    assert ledger['base_commit'] == REVIEW_BASE
    row = ledger['files'][relative]
    source = subprocess.check_output(['git', 'show', ledger['base_commit'] + ':' + relative], cwd=ROOT)
    assert hashlib.sha256(source).hexdigest() == row['before_sha256'], 'Reviewed pose preimage changed'
    candidate = path.read_bytes() if actual is None else actual
    assert hashlib.sha256(candidate).hexdigest() == row['after_sha256'], 'Pose bytes changed outside reviewed scope'
    before, current = json.loads(source), json.loads(candidate)
    restored = deepcopy(current)
    seen = set()
    assert row['operations'], 'Reviewed pose delta must be nonempty'
    for operation in row['operations']:
        keys = operation['path']
        assert tuple(keys) not in seen, 'Duplicate pose edit'
        seen.add(tuple(keys))
        assert keys[0] == 'animations' and keys[2:5] == ['bones', 'grip', 'position']
        assert len(keys) in (5, 6), 'Only exact position vectors may change'
        node = restored
        original = before
        for key in keys[:-1]:
            node, original = node[key], original[key]
        assert node[keys[-1]] == operation['after'], 'Reviewed pose postimage changed'
        assert original[keys[-1]] == operation['before'], 'Reviewed position preimage changed'
        node[keys[-1]] = operation['before']
    assert restored == before, 'Reversal left an undeclared pose change'
    return before


def historical_pose(path):
    """Earlier release identities retain their original current-tree assertions."""
    version = tuple(json.loads((ROOT / 'baseline.json').read_text())['version'])
    if version >= (2, 8, 105):
        return reviewed_before(path)
    return json.loads(Path(path).read_bytes())


def historical_bytes(path):
    """Retain original byte-for-byte historical assertions, including formatting."""
    path = Path(path)
    version = tuple(json.loads((ROOT / 'baseline.json').read_text())['version'])
    if version >= (2, 8, 105):
        reviewed_before(path)
        relative = path.relative_to(ROOT).as_posix()
        return subprocess.check_output(['git', 'show', REVIEW_BASE + ':' + relative], cwd=ROOT)
    return path.read_bytes()
