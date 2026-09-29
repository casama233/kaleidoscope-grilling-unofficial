#!/usr/bin/env python3
"""Final explicit public-family overlay; never run historical generators implicitly."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'compat/family/candidate.json').read_text())
for side,folder in cfg['packs'].items():
 p=ROOT/folder/'manifest.json';m=json.loads(p.read_text());old=cfg['baselineManifests'][side]
 assert m['header']['uuid']==old['header']['uuid']
 assert [x['uuid'] for x in m['modules']]==[x['uuid'] for x in old['modules']]
 m['header']['version']=list(map(int,cfg['version'].split('.')))
 m['header'].update(cfg.get('allowedHeaderMetadata',{}).get(side,{}))
 for mod in m['modules']:mod['version']=m['header']['version']
 m['dependencies']=cfg['expectedDependencies'][side]
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for path in cfg['profileScripts']:
 src=ROOT/'development/gameplay_core'/Path(path).name
 assert src.is_file();shutil.copyfile(src,ROOT/path)
for name,slots in [('grill',3),('advanced_rack_block',9)]:
 p=ROOT/cfg['packs']['BP']/f'blocks/{name}.json';d=json.loads(p.read_text())
 old=d['minecraft:block']['components'].pop('minecraft:block_entity',None)
 assert old is None or old=={'container':{'slot_count':slots}},'Unexpected legacy container schema'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for side,folder in cfg['packs'].items():
 for src in (ROOT/'compat/family/storage-assets'/side).rglob('*.json'):
  dst=ROOT/folder/src.relative_to(ROOT/'compat/family/storage-assets'/side)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
patch=json.loads((ROOT/'compat/family/storage-main-edits.json').read_text())
p=ROOT/patch['path'];raw=p.read_bytes()
if hashlib.sha256(raw).hexdigest()!=patch['after']:
 assert hashlib.sha256(raw).hexdigest()==patch['before'],'Main runtime changed: reconcile overlay instead of overwriting it'
 text=raw.decode()
 for a,b,value in reversed(patch['edits']):text=text[:a]+value+text[b:]
 assert hashlib.sha256(text.encode()).hexdigest()==patch['after']
 p.write_bytes(text.encode())
print('Applied Grilling '+cfg['version']+' public-host/stable-storage candidate. Run family_candidate.py.')
