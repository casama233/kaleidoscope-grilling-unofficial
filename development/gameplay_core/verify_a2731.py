from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
OLD_IMPORTS=(
 "import './a2715_canola_crop_runtime.js';",
 "import './a2717_onion_crop_runtime.js';",
 "import './a2719_sweet_potato_crop_runtime.js';",
)
NEW_IMPORT="import './a2731_farmland_crop_host_runtime.js';"

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,31] and rm['header']['version']==[2,7,31]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.31 Farmland Crop Host BP'

 core=BP/'scripts/a2731_farmland_crop_host_core.js'
 runtime=BP/'scripts/a2731_farmland_crop_host_runtime.js'
 assert core.read_bytes()==(DEV/'a2731_farmland_crop_host_core.js').read_bytes()
 assert runtime.read_bytes()==(DEV/'a2731_farmland_crop_host_runtime.js').read_bytes()

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main.count(NEW_IMPORT)==1
 assert "import './a2714_houttuynia_crop_runtime.js';" in main
 for line in OLD_IMPORTS:assert line not in main,line

 rt=runtime.read_text(encoding='utf-8')
 assert rt.count('system.beforeEvents.startup.subscribe')==1
 assert rt.count('world.afterEvents.playerBreakBlock.subscribe')==1
 assert 'for(const cfg of farmlandCropTable())' in rt
 assert 'registerCustomComponent(cfg.componentId,componentFor(cfg))' in rt
 assert "event.brokenBlockPermutation?.type?.id!=='minecraft:short_grass'" in rt
 assert 'Array.from({length:6},()=>Math.random())' in rt

 # Existing block contracts stay untouched: old worlds still address the same component IDs.
 expected={
  'canola_crop':'kaleidoscope_grilling:canola_crop_logic',
  'onion_crop':'kaleidoscope_grilling:onion_crop_logic',
  'sweet_potato_crop':'kaleidoscope_grilling:sweet_potato_crop_logic',
 }
 for block_name,component in expected.items():
  block=load(BP/f'blocks/{block_name}.json')['minecraft:block']
  assert component in block['components'],(block_name,component)
  assert block['description']['states']['kaleidoscope_grilling:age']==list(range(8))

 # Historical runtimes remain for old slice CI, but no longer execute in current main.js.
 for name in ('a2715_canola_crop_runtime.js','a2717_onion_crop_runtime.js','a2719_sweet_potato_crop_runtime.js'):
  assert (BP/'scripts'/name).is_file(),name

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2731_core.mjs')],check=True)
 for old in ('test_a2715_core.mjs','test_a2717_core.mjs','test_a2719_core.mjs','test_a2714_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/old)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2731-crop-host.json')
 assert report['version']=='A2.7.31'
 assert report['cookery_bedrock']['public_crop_extension_detected'] is False
 assert report['before']['ordinary_farmland_runtime_modules']==3
 assert report['after']['ordinary_farmland_runtime_modules']==1
 assert report['after']['registered_crop_components']==3
 assert report['after']['grass_acquisition_subscribers']==1
 assert report['houttuynia_special_runtime_retained'] is True
 assert report['component_ids_unchanged'] is True
 assert report['block_json_unchanged'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Prior host/API refactors and language fixes remain in place.
 assert "import './a2727_cookery_host_recipes_runtime.js';" in main
 assert "from './a2730_cookery_oil_pot_adapter.js';" in main
 tw=(RP/'texts/zh_TW.lang').read_text(encoding='utf-8-sig')
 assert '森羅物語：煙火' in tw and '烤饅頭片串' in tw

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.31','farmland_crop_host':True,'hosted_crops':3,
  'active_ordinary_crop_runtime_modules':1,'grass_acquisition_subscribers':1,
  'houttuynia_special_runtime_retained':True,'component_ids_unchanged':True,
  'a2730_oil_adapter_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2731-dash-verification.json' if a.compiled else 'a2731-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
