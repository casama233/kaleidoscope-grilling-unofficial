from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,51] and rm['header']['version']==[2,7,51]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.51 Pepper Forest Worldgen BP'

 feature_path=BP/'features/pepper_tree_worldgen.json'
 rule_path=BP/'feature_rules/pepper_tree_worldgen_rule.json'
 assert feature_path.read_bytes()==(DEV/'a2751_pepper_tree_worldgen.feature.json').read_bytes()
 assert rule_path.read_bytes()==(DEV/'a2751_pepper_tree_worldgen_rule.feature_rule.json').read_bytes()

 feature=load(feature_path)['minecraft:tree_feature']
 assert feature['description']['identifier']=='kaleidoscope_grilling:pepper_tree_worldgen'
 trunk=feature['acacia_trunk']
 assert trunk['trunk_width']==1
 assert trunk['trunk_height']=={'base':2,'intervals':[1],'min_height_for_canopy':2}
 assert trunk['trunk_block']['name']=='kaleidoscope_grilling:pepper_log'
 assert trunk['trunk_lean']['allow_diagonal_growth'] is False
 canopy=feature['random_spread_canopy']
 assert canopy['canopy_height']==3 and canopy['canopy_radius']==1
 assert canopy['leaf_placement_attempts']==18
 assert canopy['leaf_blocks']==[['kaleidoscope_grilling:pepper_leaves',1]]
 assert 'minecraft:water' not in feature['may_grow_on']
 assert 'minecraft:water' not in feature['may_replace']

 rule=load(rule_path)['minecraft:feature_rules']
 assert rule['description']=={
  'identifier':'kaleidoscope_grilling:pepper_tree_worldgen_rule',
  'places_feature':'kaleidoscope_grilling:pepper_tree_worldgen'
 }
 assert rule['conditions']['placement_pass']=='surface_pass'
 filters=rule['conditions']['minecraft:biome_filter']
 assert filters==[{'test':'has_biome_tag','operator':'==','value':'forest'}]
 dist=rule['distribution']
 assert dist['iterations']==1
 assert dist['scatter_chance']=={'numerator':1,'denominator':16}
 assert dist['coordinate_eval_order']=='zxy'
 assert dist['x']=={'distribution':'uniform','extent':[0,15]}
 assert dist['z']=={'distribution':'uniform','extent':[0,15]}
 assert dist['y']=='query.heightmap(variable.worldx, variable.worldz)'

 # This slice must only add worldgen data; the existing Pepper lifecycle remains the runtime.
 assert (BP/'blocks/pepper_log.json').is_file()
 assert (BP/'blocks/pepper_leaves.json').is_file()
 assert (BP/'blocks/pepper_sapling.json').is_file()
 assert (BP/'scripts/a2748_pepper_tree_runtime.js').is_file()
 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2748_pepper_tree_runtime.js';" in main_text
 assert 'a2751' not in main_text

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2751-pepper-forest-worldgen.json')
 assert report['version']=='A2.7.51'
 assert report['java']['rarity_denominator']==16
 assert report['bedrock']['scatter_chance']=={'numerator':1,'denominator':16}
 assert report['bedrock']['biome_tag']=='forest'
 assert report['bedrock']['script_runtime_added'] is False
 assert report['reuse']['duplicate_tree_blocks'] is False
 assert report['known_difference']['java_initial_fruiting_chance']==0.25
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 compiled=[]
 if a.compiled:
  dist_root=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist_root.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.51','pepper_forest_worldgen':True,'forest_tag':True,
  'rarity_denominator':16,'native_tree_feature':True,'native_feature_rule':True,
  'new_script_runtime':False,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2751-dash-verification.json' if a.compiled else 'a2751-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
