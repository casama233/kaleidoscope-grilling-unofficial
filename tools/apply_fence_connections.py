#!/usr/bin/env python3
"""Merge the server's fence-connection fixes onto a built server edition.

The server keeps per-block `minecraft:connection_rule: {accepts_connections_from:
'none'}` fixes (so crops/oil/racks/grills do not participate in neighbour
connection states) as addon_localizations replacement records under
`fence_connections/<pack-uuid>/`. When a new upstream artifact lands, those
records must be re-based onto the new files and their sha256 gates refreshed,
otherwise BSM local-install fails closed.

Usage: python tools/apply_fence_connections.py [--base DIR] [--records DIR]
                                              [--update-records] [--check]
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'build/server-edition'
RECORDS = Path('/var/lib/docker/volumes/bsm_data/_data/plugins/addon_localizations')
UUID = 'c68005c5-23ff-54e8-a3ff-da6349ad43c2'
RULE = {'accepts_connections_from': 'none'}

argv = sys.argv[1:]
def take(flag, default=None):
    if flag in argv:
        i = argv.index(flag); argv.pop(i); return argv.pop(i)
    return default
base = Path(take('--base', str(BASE)))
records = Path(take('--records', str(RECORDS)))
upstream_path = take('--upstream')
upstream = None
if upstream_path:
    import zipfile
    _z = zipfile.ZipFile(upstream_path)
    def member(z, rel):
        for cand in ('behavior_pack/' + rel, rel):
            if cand in z.namelist():
                return z.read(cand)
        raise KeyError(rel)
    upstream = _z
update = '--update-records' in argv
check = '--check' in argv

bp = base / 'behavior_pack'
index_path = records / 'index.json'
idx = json.loads(index_path.read_text(encoding='utf-8'))
recs = [r for r in idx['luosen'] if r.get('uuid') == UUID and 'fence_connections' in str(r.get('replacement'))]
assert recs, 'no fence_connections records for ' + UUID

merged = 0; already = 0; updated = 0
for r in recs:
    rel = r['path']
    f = bp / rel
    assert f.is_file(), f
    j = json.loads(f.read_text(encoding='utf-8'))
    block = j['minecraft:block']
    comps = block.setdefault('components', {})
    if comps.get('minecraft:connection_rule') == RULE:
        already += 1; continue
    comps['minecraft:connection_rule'] = dict(RULE)
    f.write_text(json.dumps(j, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    merged += 1
if update:
    assert upstream, '--update-records needs --upstream <artifact.mcaddon>'
    for r in recs:
        f = bp / r['path']
        repl = records / r['replacement']
        repl.write_bytes(f.read_bytes())
        # Gate baseline = the pristine upstream artifact's hash, so installing a
        # future upstream release that changes the file still fails closed while
        # installing this build (or the original 2.8.7 artifact) passes.
        r['sha256'] = hashlib.sha256(member(upstream, r['path'])).hexdigest()
        updated += 1
    index_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'connection_rule merged={merged} already={already}' + (f' records-refreshed={updated}' if update else ''))
if check:
    for r in recs:
        f = bp / r['path']
        j = json.loads(f.read_text(encoding='utf-8'))
        assert j['minecraft:block']['components'].get('minecraft:connection_rule') == RULE, r['path']
    print('check OK: all', len(recs), 'files carry the connection rule')
