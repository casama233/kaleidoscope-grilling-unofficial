"""Canonical stable-BDS runtime regressions. Client acceptance remains separate."""
from pathlib import Path
import json,os,subprocess,sys,tempfile
from verify_current import ROOT,BP,RP,generic_gate
from verify_a287 import binding_assets
from verify_a284 import eating_gate
from verify_a285 import survival_gate
from verify_a283 import assets,feedback

def main():
 generic_gate();binding_assets();eating_gate();survival_gate();assets();feedback()
 for file in (BP/'scripts').rglob('*.js'):subprocess.run(['node','--check',str(file)],check=True,capture_output=True)
 subprocess.run(['node',str(Path(__file__).with_name('test_a2810_use.mjs'))],cwd=ROOT,check=True,env={**os.environ,'GRILLING_USE_BASE':'7ef78bb360ac6a34664a15deef2c2aff5cc3d719'})
 scripts=BP/'scripts'
 assert (scripts/'itemData.js').is_file() and (scripts/'blockSupport.js').is_file()
 assert not (scripts/'guide.js').exists() and not (scripts/'guidePublisher.js').exists()
 assert (scripts/'main.js').read_text().count("import './guide/main.js';")==1
 for name in ['main.js','a25_plate_recipe_runtime.js']:assert '.isSolid' not in (scripts/name).read_text()
 for file in (BP/'blocks').glob('*.json'):
  obj=json.loads(file.read_text())['minecraft:block']
  for comp in [obj['components']]+[p['components'] for p in obj.get('permutations',[])]:
   assert 'tag:minecraft:crop' not in comp
   for v in comp.get('minecraft:material_instances',{}).values():
    if isinstance(v,dict) and 'ambient_occlusion' in v:assert not isinstance(v['ambient_occlusion'],bool)
 for name in ['canola_seeds','houttuynia','onion','sweet_potato']:assert json.loads((BP/f'items/{name}.json').read_text())['minecraft:item']['description']['menu_category']['category']=='nature'
 print('A2.8.11 canonical stable API, source bindings and transaction regressions PASS; client acceptance not run')
if __name__=='__main__':main()
