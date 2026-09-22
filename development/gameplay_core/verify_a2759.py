from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
CORE='a2759_pepper_worldgen_fruiting_core.js'
RUNTIME='a2759_pepper_worldgen_fruiting_runtime.js'
BLOCK='pepper_leaves_fruiting_bridge.json'
FEATURE='pepper_tree_worldgen.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,59] and rm['header']['version']==[2,7,59]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.59 P1 Completion BP'

 assert (BP/'scripts'/CORE).read_bytes()==(DEV/CORE).read_bytes()
 assert (BP/'scripts'/RUNTIME).read_bytes()==(DEV/RUNTIME).read_bytes()
 assert (BP/'blocks'/BLOCK).read_bytes()==(DEV/'a2759_pepper_leaves_fruiting_bridge.block.json').read_bytes()
 assert (BP/'features'/FEATURE).read_bytes()==(DEV/'a2759_pepper_tree_worldgen.feature.json').read_bytes()

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2759_pepper_worldgen_fruiting_runtime.js';")==1
 assert main_text.index("import './a2748_pepper_tree_runtime.js';")<main_text.index("import './a2759_pepper_worldgen_fruiting_runtime.js';")

 feature=load(BP/'features'/FEATURE)['minecraft:tree_feature']
 leaves=feature['random_spread_canopy']['leaf_blocks']
 assert leaves==[
  ['kaleidoscope_grilling:pepper_leaves',3],
  ['kaleidoscope_grilling:pepper_leaves_fruiting_bridge',1]
 ]
 assert feature['random_spread_canopy']['canopy_height']==3
 assert feature['random_spread_canopy']['canopy_radius']==1
 assert feature['random_spread_canopy']['leaf_placement_attempts']==18

 block=load(BP/'blocks'/BLOCK)['minecraft:block']
 assert block['description']['identifier']=='kaleidoscope_grilling:pepper_leaves_fruiting_bridge'
 assert 'menu_category' not in block['description']
 comps=block['components']
 assert comps['minecraft:geometry']=='geometry.kg_a1.pepper_leaves_fruiting'
 assert comps['minecraft:material_instances']['*']['texture']=='kg_a2748_pepper_leaves_fruiting'
 assert comps['minecraft:tick']=={'interval_range':[1,1],'looping':False}
 assert 'kaleidoscope_grilling:pepper_worldgen_fruiting_bridge' in comps
 assert 'minecraft:loot' not in comps
 assert not (BP/'items'/'pepper_leaves_fruiting_bridge.json').exists()

 runtime=(BP/'scripts'/RUNTIME).read_text(encoding='utf-8')
 for token in (
  'PEPPER_WORLDGEN_FRUITING_COMPONENT_ID',
  'event.blockComponentRegistry.registerCustomComponent',
  'onTick(e)',
  'BlockPermutation.resolve(PEPPER_LEAVES_ID',
  '[PEPPER_HAS_STATE]:true',
  '[PEPPER_PERSISTENT_STATE]:false'
 ):
  assert token in runtime,token
 for forbidden in ('runInterval','getAllPlayers','getEntities','onRandomTick'):
  assert forbidden not in runtime,forbidden

 core=(BP/'scripts'/CORE).read_text(encoding='utf-8')
 for token in (
  'PEPPER_WORLDGEN_NORMAL_WEIGHT=3',
  'PEPPER_WORLDGEN_FRUITING_WEIGHT=1',
  'worldgenFruitingProbability',
  'worldgenLeafWeights'
 ):
  assert token in core,token

 # P1 Advanced Rack remains complete and present.
 rack=(BP/'scripts/a2746_advanced_rack_core.js').read_text(encoding='utf-8')
 assert 'RACK_COMPARTMENTS=9' in rack
 assert 'RACK_SEASONING_SLOTS=5' in rack and 'RACK_TOOL_SLOTS=4' in rack
 rack_runtime=(BP/'scripts/a2746_advanced_rack_runtime.js').read_text(encoding='utf-8')
 for token in ('depositMatching(','swapWithHotbar(','customCommandRegistry.registerCommand','writeRackPayloadItem','readRackPayloadItem'):
  assert token in rack_runtime,token
 automation=(BP/'scripts/a2746_rack_automation_api.js').read_text(encoding='utf-8')
 assert 'export function borrowAdvancedRackItem' in automation
 assert 'export function returnAdvancedRackItem' in automation

 # Preserve Pepper lifecycle/acquisition chain.
 pepper_runtime=(BP/'scripts/a2748_pepper_tree_runtime.js').read_text(encoding='utf-8')
 for token in ('shouldFruitPepperLeaf','harvestedPepperCount','onStepOn(event){sting(event.entity)}','saplingBonemealSucceeds','pepperTreePlan'):
  assert token in pepper_runtime,token
 assert 'system.runInterval(' not in pepper_runtime
 rule=load(BP/'feature_rules/pepper_tree_worldgen_rule.json')['minecraft:feature_rules']
 assert rule['distribution']['scatter_chance']=={'numerator':1,'denominator':16}
 assert any(x.get('value')=='forest' for x in rule['conditions']['minecraft:biome_filter'])
 assert (BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json').is_file()
 assert (BP/'scripts/a2753_advancement_runtime.js').is_file()

 subprocess.run(['node',str(DEV/'test_a2759_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2759-p1-completion.json')
 assert report['version']=='A2.7.59'
 assert report['advanced_rack']['complete'] is True
 assert report['advanced_rack']['automation_borrow_return'] is True
 assert report['pepper_tree']['worldgen_initial_fruiting_probability']==0.25
 assert report['pepper_tree']['worldgen_leaf_weights']==[3,1]
 assert report['pepper_tree']['worldgen_bridge_is_internal'] is True
 assert report['pepper_tree']['worldgen_bridge_canonicalizes_after_ticks']==1
 assert report['platform_limit']['bedrock_stable_on_entity_inside'] is False
 assert report['platform_limit']['global_entity_leaf_polling_added'] is False
 assert report['p1_actionable_complete'] is True
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
  'version':'A2.7.59','p1_actionable_complete':True,
  'advanced_rack_complete':True,'pepper_tree_complete':True,
  'worldgen_initial_fruiting_probability':0.25,
  'worldgen_leaf_weights':[3,1],
  'worldgen_bridge_internal':True,'worldgen_bridge_one_shot_tick':True,
  'entity_inside_platform_limit':True,'global_entity_leaf_polling_added':False,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2759-dash-verification.json' if a.compiled else 'a2759-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
