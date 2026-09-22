from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SOURCE_RP=ROOT/'projects/grilling/resource_pack'
NEW=('a2746_advanced_rack_core.js','a2746_advanced_rack_runtime.js')
GEOS=tuple(f'advanced_rack_{i}.geo.json' for i in range(5))
LANG_KEYS=(
 'tile.kaleidoscope_grilling:advanced_rack.name',
 'container.kaleidoscope_grilling.advanced_rack',
 'container.kaleidoscope_grilling.advanced_rack_shortcut',
 'tooltip.kaleidoscope_grilling.advanced_rack.saved_contents',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,46] and rm['header']['version']==[2,7,46]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.46 Advanced Rack Foundation BP'
 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2746_advanced_rack_runtime.js';")==1

 block=load(BP/'blocks/advanced_rack.json')
 expected=load(DEV/'a2746_advanced_rack.block.json')
 assert block==expected
 desc=block['minecraft:block']['description'];components=block['minecraft:block']['components']
 assert desc['identifier']=='kaleidoscope_grilling:advanced_rack'
 assert desc['states']['kaleidoscope_grilling:spice_level']==[0,1,2,3,4]
 assert components['minecraft:block_entity']['container']['slot_count']==9
 assert components['minecraft:geometry']=='geometry.kg_a1.advanced_rack_0'
 perms=block['minecraft:block']['permutations']
 for i in range(5):
  token=f"q.block_state('kaleidoscope_grilling:spice_level') == {i}"
  rows=[x for x in perms if x['condition']==token];assert len(rows)==1,(i,rows)
  assert rows[0]['components']['minecraft:geometry']==f'geometry.kg_a1.advanced_rack_{i}'

 terrain=load(RP/'textures/terrain_texture.json')
 assert terrain['texture_data']['kg_a2746_advanced_rack']=={'textures':'textures/blocks/advanced_rack'}
 for name in GEOS:
  actual=RP/'models/blocks'/name;source=SOURCE_RP/'models/entity/kg_a1'/name
  assert actual.read_bytes()==source.read_bytes(),name
  geo=load(actual);identifier=geo['minecraft:geometry'][0]['description']['identifier']
  assert identifier==f"geometry.kg_a1.{name.removesuffix('.geo.json')}",identifier
 assert (RP/'textures/blocks/advanced_rack.png').read_bytes()==(SOURCE_RP/'textures/kg_a1/advanced_rack.png').read_bytes()

 core=(BP/'scripts/a2746_advanced_rack_core.js').read_text(encoding='utf-8')
 for token in (
  "from './a2734_cookery_oil_pot_core.js'",
  "from './a2743_seasoning_contract_core.js'",
  "from './data.js'",
  'RACK_COMPARTMENT_COUNT=9','RACK_SEASONING_SLOTS=5','RACK_TOOL_SLOTS=4',
  "COOKERY_KNIFE_TAG='kaleidoscope_cookery:kitchen_knife'",
  "COOKERY_SHOVEL_TAG='kaleidoscope_cookery:kitchen_shovel'",
  'rackCanPlaceWithFilter','rackFiltersAfterInsert','rackCanClearFilter','rackSpiceLevel'
 ):
  assert token in core,token

 runtime=(BP/'scripts/a2746_advanced_rack_runtime.js').read_text(encoding='utf-8')
 for token in ('a2746RackInventory','a2746ReadRackFilters','a2746WriteRackFilters','a2746RackCanPlace','a2746RackSetItem','a2746RackClearFilter','a2746SyncRackDisplay','a2746RackSnapshot'):
  assert token in runtime,token
 assert "getComponent('minecraft:inventory')" in runtime
 assert 'system.runInterval' not in runtime

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2746_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2746-advanced-rack-foundation.json')
 assert report['version']=='A2.7.46'
 assert report['java_contract']['compartments']==9
 assert report['java_contract']['seasoning_slots']==5
 assert report['java_contract']['tool_slots']==4
 assert report['reuse']['native_block_container'] is True
 assert report['reuse']['duplicate_item_whitelist'] is False
 assert 'menu_screen' in report['deferred']
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

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
  'version':'A2.7.46','advanced_rack_foundation':True,'native_container_slots':9,
  'shared_oil_and_seasoning_contracts':True,'cookery_tool_tags':True,
  'preconverted_visuals_reused':True,'menu_screen_deferred':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2746-dash-verification.json' if a.compiled else 'a2746-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
