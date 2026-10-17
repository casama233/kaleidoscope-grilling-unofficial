"""Completion safety and server-edition regressions; no client render claim."""
from pathlib import Path
import json, os, subprocess, sys, tempfile, zipfile
from verify_current import ROOT, BP, RP
from verify_a287 import plant_gate, binding_assets
from verify_a284 import eating_gate
from verify_a285 import survival_gate
from verify_a283 import main as previous_gate
BASE='7ef78bb360ac6a34664a15deef2c2aff5cc3d719'

def server_edition_gate():
 with tempfile.TemporaryDirectory() as temp:
  temp=Path(temp);artifact=temp/'Kaleidoscope_Grilling_A2.8.10.mcaddon';out=temp/'server'
  with zipfile.ZipFile(artifact,'w',zipfile.ZIP_DEFLATED) as z:
   for root in (BP,RP):
    for f in sorted(root.rglob('*')):
     if f.is_file():z.write(f,root.name+'/'+f.relative_to(root).as_posix())
  result=subprocess.run([sys.executable,str(ROOT/'tools/build_server_edition.py'),'--artifact',str(artifact),'--version','2.8.10',str(out)],text=True,capture_output=True)
  assert result.returncode==0,result.stdout+result.stderr
  scripts=out/'behavior_pack/scripts'
  assert not (scripts/'guide.js').exists() and not (scripts/'guidePublisher.js').exists()
  main=(scripts/'main.js').read_text()
  assert main.count("import './guide/main.js';")==1
  for f in (BP/'scripts/guide').glob('*.js'):assert (scripts/'guide'/f.name).read_bytes()==f.read_bytes(),f
  # Replacement stack writes must use the stable stackable-item adapter as well.
  assert 'setItemProperty(out,SEASON_VARIANT_KEY,variant)' in main
  assert 'getItemLore(stack)' in (scripts/'a285_eating_transaction.js').read_text()
  for side in ('behavior_pack','resource_pack'):
   m=json.loads((out/side/'manifest.json').read_text());assert m['header']['version']==[2,8,10]
   assert all(x['version']==[2,8,10] for x in m['modules'])
   cookery=[d for d in m['dependencies'] if d.get('uuid') in ('403f7a4a-a837-42c8-b5d3-76d5079ef269','8f39983b-00a6-4818-b489-0a73daf3bc87')]
   assert len(cookery)==1 and cookery[0]['version']==[1,0,7]
  bp=json.loads((out/'behavior_pack/manifest.json').read_text())
  assert next(d for d in bp['dependencies'] if d.get('uuid')=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389')['version']==[2,8,10]
  for name in ('grill','pepper_leaves','seasoning_bottle_4','advanced_rack_block'):
   b=json.loads((out/f'behavior_pack/blocks/{name}.json').read_text())['minecraft:block']
   assert b['components']['minecraft:connection_rule']=={'accepts_connections_from':'none'}
  for name in ('canola_seeds','houttuynia','onion','sweet_potato'):
   i=json.loads((out/f'behavior_pack/items/{name}.json').read_text())['minecraft:item']
   assert i['description']['menu_category']['category']=='nature'
  for f in scripts.rglob('*.js'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True)
 print('A2810 server edition: one canonical guide, stable item adapters, paired versions PASS')

if __name__=='__main__':
 subprocess.run(['node',str(Path(__file__).with_name('test_a2810_use.mjs'))],cwd=ROOT,check=True,env={**os.environ,'GRILLING_USE_BASE':BASE})
 server_edition_gate();binding_assets();plant_gate();eating_gate();survival_gate();previous_gate()
