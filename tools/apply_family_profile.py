#!/usr/bin/env python3
"""Apply the reviewed public-family candidate after the existing Grilling generator.
Preserves headers/modules and data; never runs the historical generators itself.
"""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[1];cfg=json.loads((ROOT/'compat/family/candidate.json').read_text())
for side,folder in cfg['packs'].items():
 p=ROOT/folder/'manifest.json';m=json.loads(p.read_text());old=cfg['baselineManifests'][side]
 assert m['header']['uuid']==old['header']['uuid']
 assert [x['uuid'] for x in m['modules']]==[x['uuid'] for x in old['modules']]
 m['header']['version']=[2,8,8]
 for mod in m['modules']:mod['version']=[2,8,8]
 m['dependencies']=cfg['expectedDependencies'][side]
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
for path in cfg['allowedRuntimeChanges']:
 if '/scripts/' not in path:continue
 src=ROOT/'development/gameplay_core'/Path(path).name
 assert src.is_file();shutil.copyfile(src,ROOT/path)
print('Applied reviewed 2.8.8 public profile; run family_candidate.py before packaging.')
