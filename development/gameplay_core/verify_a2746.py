from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SCRIPTS=(
 'a2746_advanced_rack_core.js','a2746_rack_item_codec.js','a2746_rack_state_adapter.js',
 'a2746_rack_automation_api.js','a2746_advanced_rack_runtime.js'
)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,46] and rm['header']['version']==[2,7,46]
 assert any(d.get('module_name')=='@minecraft/server-ui' and d.get('version')=='2.2.0' for d in bm['dependencies'])
 for name in SCRIPTS:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 assert (BP/'blocks/advanced_rack_block.json').read_bytes()==(DEV/'a2746_advanced_rack_block.json').read_bytes()
 assert (BP/'items/advanced_rack.json').read_bytes()==(DEV/'a2746_advanced_rack_item.json').read_bytes()
 assert (BP/'recipes/advanced_rack.json').read_bytes()==(DEV/'a2746_advanced_rack_recipe.json').read_bytes()

 block=load(BP/'blocks/advanced_rack_block.json')['minecraft:block']
 assert block['description']['states']['kaleidoscope_grilling:spice_level']==[0,1,2,3,4]
 assert block['components']['minecraft:block_entity']['container']['slot_count']==9
 item=load(BP/'items/advanced_rack.json')['minecraft:item']
 assert item['components']['minecraft:max_stack_size']==1
 assert item['components']['minecraft:block_placer']['block']=='kaleidoscope_grilling:advanced_rack_block'
 recipe=load(BP/'recipes/advanced_rack.json')['minecraft:recipe_shaped']
 assert recipe['pattern']==['III',' R ','SSS']
 assert recipe['key']['R']['item']=='kaleidoscope_cookery:kitchenware_racks'

 for i in range(5):
  geo=load(RP/f'models/blocks/advanced_rack_{i}.geo.json')
  assert geo['minecraft:geometry'][0]['description']['identifier']==f'geometry.kg_a1.advanced_rack_{i}'
 assert (RP/'textures/blocks/advanced_rack.png').is_file()
 assert load(RP/'textures/terrain_texture.json')['texture_data']['kg_a2746_advanced_rack']['textures']=='textures/blocks/advanced_rack'
 assert load(RP/'textures/item_texture.json')['texture_data']['advanced_rack']['textures']=='textures/blocks/advanced_rack'

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2746_advanced_rack_runtime.js';")==1
 runtime=(BP/'scripts/a2746_advanced_rack_runtime.js').read_text(encoding='utf-8')
 for token in ('ActionFormData','registerCommand','kaleidoscope_grilling:rack','depositMatching','swapWithHotbar',
               'world.beforeEvents.playerBreakBlock','world.beforeEvents.explosion','readRackPayloadItem','writeRackPayloadItem'):
  assert token in runtime,token
 assert runtime.count('new ActionFormData()')>=2
 assert 'system.runInterval(' not in runtime

 codec=(BP/'scripts/a2746_rack_item_codec.js').read_text(encoding='utf-8')
 for token in ('getDynamicPropertyIds','getRawLore','ItemComponentTypes.Durability','ItemComponentTypes.Enchantable','EnchantmentType','getCanDestroy','getCanPlaceOn'):
  assert token in codec,token
 assert 'minecraft:storage_item' not in codec

 api=(BP/'scripts/a2746_rack_automation_api.js').read_text(encoding='utf-8')
 assert 'borrowAdvancedRackItem' in api and 'returnAdvancedRackItem' in api

 subprocess.run(['node',str(DEV/'test_a2746_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 report=load(P/'reports/a2746-advanced-rack.json')
 assert report['version']=='A2.7.46'
 assert report['java']['compartments']==9 and report['java']['seasoning_slots']==5 and report['java']['tool_slots']==4
 assert report['java']['break_preserves_contents'] is True and report['java']['automation_api'] is True
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
 result={'version':'A2.7.46','advanced_rack':True,'compartments':9,'persistent_filters':True,'deposit_matching':True,
  'hotbar_binding':True,'automation_api':True,'break_preserves_contents':True,'models_reused':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2746-dash-verification.json' if a.compiled else 'a2746-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text())
if __name__=='__main__':main()
