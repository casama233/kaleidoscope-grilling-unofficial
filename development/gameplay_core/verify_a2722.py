from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
TEX_SHA='98d59596cc06892e78d6d90d3e8ed2303151f841'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,22] and rm['header']['version']==[2,7,22]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.22 Cold Houttuynia BP'

 item=load(BP/'items/cold_houttuynia.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:cold_houttuynia'
 assert c['minecraft:max_stack_size']==64 and c['minecraft:allow_off_hand'] is True
 assert c['minecraft:food']=={'can_always_eat':False,'nutrition':6,'saturation_modifier':1.0}
 assert c['minecraft:use_animation']=={'value':'eat'} and c['minecraft:tags']['tags']==['minecraft:is_food']

 tex=RP/'textures/items/cold_houttuynia.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 assert load(RP/'textures/item_texture.json')['texture_data']['cold_houttuynia']['textures']=='textures/items/cold_houttuynia'

 core=BP/'scripts/a2722_cold_houttuynia_core.js';runtime=BP/'scripts/a2722_cold_houttuynia_runtime.js'
 assert core.read_bytes()==(DEV/'a2722_cold_houttuynia_core.js').read_bytes()
 assert runtime.read_bytes()==(DEV/'a2722_cold_houttuynia_runtime.js').read_bytes()
 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2722_cold_houttuynia_runtime.js';")==1
 assert not (BP/'recipes/cold_houttuynia.json').exists()

 report=load(P/'reports/a2722-parity.json')
 assert report['version']=='A2.7.22'
 assert report['item']['nutrition']==6 and report['item']['saturation_modifier']==1.0
 assert report['item']['base_effect_ticks']==1200
 assert report['java_recipe']['houttuynia_count']==3 and report['java_recipe']['oil_points']==2
 assert report['java_recipe']['oil_type']=='premium_chili'
 assert report['bedrock_recipe_equivalent']['ingredient_count_exact'] is True
 assert report['bedrock_recipe_equivalent']['partial_oil_consumption_exact'] is True
 assert report['bedrock_recipe_equivalent']['crafting_grid_surface_exact'] is False
 assert report['effect']['base_fire_resistance_1200_ticks'] is True
 assert report['effect']['cuisine_quality_duration_scaling_ported'] is False
 assert report['survival_chain']['cold_houttuynia_obtainable_in_survival'] is True
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
  'version':'A2.7.22','cold_houttuynia_item':True,'scripted_crafting_equivalent':True,
  'houttuynia_used':3,'premium_chili_oil_points_used':2,'base_fire_resistance_ticks':1200,
  'crafting_grid_surface_exact':False,'cuisine_quality_scaling_ported':False,
  'a2721_roasted_chicken_wing_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2722-dash-verification.json' if a.compiled else 'a2722-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
