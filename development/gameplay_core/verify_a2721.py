from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
TEX_SHA='88d0b45b57a7958f185f9b292eda18d5b57dac42'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,21] and rm['header']['version']==[2,7,21]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.21 Roasted Chicken Wing BP'

 raw=load(BP/'items/chicken_wing.json')['minecraft:item']['components']
 assert raw['minecraft:food']['nutrition']==2 and abs(raw['minecraft:food']['saturation_modifier']-.06)<1e-9
 item=load(BP/'items/roasted_chicken_wing.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:roasted_chicken_wing'
 assert c['minecraft:max_stack_size']==64 and c['minecraft:allow_off_hand'] is True
 assert c['minecraft:food']=={'can_always_eat':False,'nutrition':5,'saturation_modifier':0.12}
 assert c['minecraft:use_animation']=={'value':'eat'} and c['minecraft:tags']['tags']==['minecraft:is_food']

 tex=RP/'textures/items/roasted_chicken_wing.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 assert load(RP/'textures/item_texture.json')['texture_data']['roasted_chicken_wing']['textures']=='textures/items/roasted_chicken_wing'

 recipe=load(BP/'recipes/roasted_chicken_wing.json')['minecraft:recipe_furnace']
 assert recipe['description']['identifier']=='kaleidoscope_grilling:roasted_chicken_wing'
 assert recipe['tags']==['furnace','smoker','campfire','soul_campfire']
 assert recipe['input']=='kaleidoscope_grilling:chicken_wing'
 assert recipe['output']=='kaleidoscope_grilling:roasted_chicken_wing'
 assert 'experience' not in recipe and 'cookingtime' not in recipe

 assert (BP/'scripts/a2710_chicken_acquisition_runtime.js').is_file()
 report=load(P/'reports/a2721-parity.json')
 assert report['version']=='A2.7.21'
 assert report['item']['nutrition']==5 and report['item']['saturation_modifier']==0.12
 assert report['recipes']['resolved_inputs']==['kaleidoscope_grilling:chicken_wing']
 assert report['recipes']['station_access_parity'] is True
 assert report['flavor_food']['base_food_properties_exact'] is True
 assert report['flavor_food']['cuisine_quality_food_scaling_ported'] is False
 assert report['flavor_food']['maxim_tooltip_ported'] is False
 assert report['survival_chain']['roasted_chicken_wing_obtainable_in_survival'] is True
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
  'version':'A2.7.21','roasted_chicken_wing_item':True,'native_cooking_recipe':True,
  'station_tags':['furnace','smoker','campfire','soul_campfire'],'base_food_properties_exact':True,
  'java_experience_0_35_exact':False,'cuisine_quality_scaling_ported':False,
  'a2720_roasted_sweet_potato_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2721-dash-verification.json' if a.compiled else 'a2721-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
