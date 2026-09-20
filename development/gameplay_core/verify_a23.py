from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 report=load(P/'reports/build.json');a23=load(P/'reports/a23-build.json')
 assert report['version']=='A2.3.0' and a23['version']=='A2.3.0'
 assert report['formal_food_max_stack']==64 and report['normal_storage_heat_window_ticks']==6000
 assert report['grill_visual_states']==['flat_unlit','flat_lit','legged_unlit','legged_lit']
 assert report['grill_lit_light_emission']==13
 assert report['dragon_blood_effective_bonus_hp']==[6,10] and report['dragon_blood_native_visible_bonus_hp']==[4,8] and report['dragon_blood_virtual_pool_hp']==2
 assert report['world_oil_simulation'] is True and report['world_oil_levels']==8 and report['true_engine_liquid_type'] is False
 assert report['numb_crosshair'].startswith('not implemented')
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,3,0] and rm['header']['version']==[2,3,0]
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']
 foods=[]
 for p in (BP/'items').glob('*.json'):
  d=load(p)['minecraft:item'];c=d['components']
  if 'minecraft:food' in c:foods.append(p.stem);assert c['minecraft:max_stack_size']==64,(p,c['minecraft:max_stack_size'])
 assert len(foods)==41,len(foods)
 grill=load(BP/'blocks/grill.json')['minecraft:block'];states=grill['description']['states']
 assert states['kaleidoscope_grilling:legged']==[False,True] and states['kaleidoscope_grilling:lit']==[False,True]
 visual=[]
 for perm in grill['permutations']:
  cond=perm['condition']
  if 'kaleidoscope_grilling:legged' in cond:
   visual.append(perm);comp=perm['components'];assert comp['minecraft:geometry'].startswith('geometry.kg_a23.grill_')
 assert len(visual)==4
 assert sorted(p.name for p in (RP/'models/blocks').glob('grill_*geo.json'))==['grill_flat.geo.json','grill_flat_lit.geo.json','grill_legged.geo.json','grill_legged_lit.geo.json']
 assert max(x['components']['minecraft:light_emission'] for x in visual)==13
 assert any(x['components']['minecraft:material_instances']['*'].get('face_dimming') is False for x in visual)
 for typ,light in [('canola',0),('secret_chili',0),('premium_chili',15)]:
  b=load(BP/f'blocks/{typ}_oil.json')['minecraft:block'];assert b['description']['states']['kaleidoscope_grilling:level']==list(range(8))
  assert b['components']['minecraft:collision_box'] is False and 'minecraft:replaceable' in b['components']
  assert b['components']['minecraft:light_emission']==light
  assert len([x for x in b['permutations'] if "kaleidoscope_grilling:level" in x['condition']])==8
  assert (BP/f'items/{typ}_oil_bucket.json').is_file()
 oilgeo=load(RP/'models/blocks/a23_oil_levels.geo.json')['minecraft:geometry'];assert len(oilgeo)==8
 for name in ('a23_hot_merge.js','a23_hot_runtime.js','a23_oil_world.js'):assert (BP/'scripts'/name).is_file()
 runtime=(BP/'scripts/main.js').read_text()
 for token in ("mergeIntoContainer","compactSkewerContainer","syncGrillPermutation","kaleidoscope_grilling:dragon_pool","fleeCreepers","repelPhantoms","tundraFactor"):assert token in runtime,token
 hot=(BP/'scripts/a23_hot_runtime.js').read_text()
 for token in ("NORMAL_HEAT_WINDOW","weightedHeat","getDynamicPropertyIds","maxAmount","compactSkewerContainer"):assert token in hot,token
 oil=(BP/'scripts/a23_oil_world.js').read_text()
 for token in ("MAX_CELLS=160","BlockPermutation.resolve","kc_oil_count","oil_pot_filled","premium_chili"):assert token in oil,token
 assert not (RP/'ui/hud_screen.json').exists(), 'unsafe global HUD override must not be added for Numb crosshair'
 for p in BP.glob('scripts/*.js'):subprocess.run(['node','--check',str(p)],check=True)
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 result={'version':'A2.3.0','formal_foods':41,'max_stack_size':64,'hot_merge_window_ticks':6000,'grill_visual_states':4,'grill_lit_light_emission':13,'dragon_blood_effective_hp':[6,10],'numb_crosshair_safe_override':False,'world_oil_types':3,'world_oil_levels':8,'true_engine_liquid_type':False,'server_module':'2.9.0','compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a23-dash-verification.json' if a.compiled else 'a23-structure-verification.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(out.read_text())

if __name__=='__main__':main()
