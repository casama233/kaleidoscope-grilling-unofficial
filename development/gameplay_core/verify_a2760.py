from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
FEATURE='pepper_tree_worldgen.json'
SOURCE='a2760_pepper_tree_worldgen.feature.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()

 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,60] and rm['header']['version']==[2,7,60]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.60 Pepper Worldgen BDS Fix BP'

 feature_path=BP/'features'/FEATURE
 assert feature_path.read_bytes()==(DEV/SOURCE).read_bytes()

 feature=load(feature_path)['minecraft:tree_feature']
 assert feature['description']['identifier']=='kaleidoscope_grilling:pepper_tree_worldgen'
 trunk=feature['acacia_trunk']
 assert trunk['trunk_width']==1
 assert trunk['trunk_height']=={'base':2,'intervals':[1],'min_height_for_canopy':2}
 assert trunk['trunk_block']=={'name':'kaleidoscope_grilling:pepper_log'}
 lean=trunk['trunk_lean']
 assert lean['allow_diagonal_growth'] is False
 assert lean['lean_height']=={'base':1,'intervals':[1],'min_height_for_canopy':2}
 assert lean['lean_steps']=={'base':1,'intervals':[1]}
 assert set(lean)=={'allow_diagonal_growth','lean_height','lean_steps'}

 canopy=feature['random_spread_canopy']
 assert canopy['canopy_height']==3
 assert canopy['canopy_radius']==1
 assert canopy['leaf_placement_attempts']==18
 assert canopy['leaf_blocks']==[
  ['kaleidoscope_grilling:pepper_leaves',3],
  ['kaleidoscope_grilling:pepper_leaves_fruiting_bridge',1]
 ]

 # A2.7.59 P1 fruiting/lifecycle behavior must remain untouched.
 assert (BP/'scripts/a2759_pepper_worldgen_fruiting_core.js').is_file()
 assert (BP/'scripts/a2759_pepper_worldgen_fruiting_runtime.js').is_file()
 bridge=load(BP/'blocks/pepper_leaves_fruiting_bridge.json')['minecraft:block']
 assert bridge['description']['identifier']=='kaleidoscope_grilling:pepper_leaves_fruiting_bridge'
 assert bridge['components']['minecraft:tick']=={'interval_range':[1,1],'looping':False}
 assert 'kaleidoscope_grilling:pepper_worldgen_fruiting_bridge' in bridge['components']

 pepper=(BP/'scripts/a2748_pepper_tree_runtime.js').read_text(encoding='utf-8')
 assert 'system.runInterval(' not in pepper
 for token in ('shouldFruitPepperLeaf','harvestedPepperCount','saplingBonemealSucceeds','pepperTreePlan'):
  assert token in pepper,token

 # Preserve previous high-value slices.
 for path in (
  BP/'scripts/a2746_advanced_rack_runtime.js',
  BP/'scripts/a2753_advancement_runtime.js',
  BP/'scripts/a2756_advancement_event_runtime.js',
  BP/'scripts/a2758_advancement_challenge_runtime.js',
  BP/'scripts/a2750_food_state_adapter.js',
  BP/'loot_tables/kaleidoscope_grilling/village_pepper_bonus.json',
  BP/'loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json',
 ):
  assert path.is_file(),path

 adapter=(BP/'scripts/a2750_food_state_adapter.js').read_text(encoding='utf-8')
 apply=adapter.split('export function applyFoodMetadata',1)[1]
 assert apply.index('setHotFood(stack,hotTicks)')<apply.index('setFoodSeasonings(stack,seasoning)')

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2760-pepper-worldgen-bds-fix.json')
 assert report['version']=='A2.7.60'
 assert report['bug']['previous_missing']==['lean_height','lean_steps']
 assert report['bug']['source_pack_was_affected'] is True
 assert report['fix']['worldgen_leaf_weights']==[3,1]
 assert report['fix']['initial_fruiting_probability']==0.25
 assert report['official_reference']['git_blob']=='dfb66d2371e818bea6bfffb1c1785d956a76b6d6'
 assert report['prior_server_shim_bds_tested'] is True
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
  'version':'A2.7.60','pepper_worldgen_bds_fix':True,
  'lean_height_present':True,'lean_steps_present':True,
  'worldgen_leaf_weights':[3,1],'initial_fruiting_probability':0.25,
  'server_shim_becomes_noop_for_trunk_lean':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False,'prior_server_shim_bds_tested':True
 }
 out=P/'reports'/('a2760-dash-verification.json' if a.compiled else 'a2760-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
