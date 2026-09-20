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
 report=load(P/'reports/build.json');a24=load(P/'reports/a24-build.json')
 assert report['version']=='A2.4.0' and a24['version']=='A2.4.0'
 assert report['configured_skewer_recipes']==20 and report['hand_threading'] is True
 assert report['unfinished_skewer'] is True and report['secret_skewer'] is True and report['raw_skewer_disassembly'] is True
 assert report['typed_oil_pot_capacity']==64 and report['cookery_fat_capacity']==256 and report['typed_oil_bucket_points']==8
 assert report['allow_skewers_at_full_hunger'] is True
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,4,0] and rm['header']['version']==[2,4,0]
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']
 foods=[]
 for p in (BP/'items').glob('*.json'):
  d=load(p)['minecraft:item'];c=d['components']
  if 'minecraft:food' in c:
   foods.append(p.stem)
   assert c['minecraft:max_stack_size']==64,(p,c['minecraft:max_stack_size'])
   assert c['minecraft:food']['can_always_eat'] is True,(p,c['minecraft:food'])
 assert len(foods)==42,len(foods)
 unfinished=load(BP/'items/unfinished_skewer.json')['minecraft:item']['components']
 secret=load(BP/'items/secret_skewer.json')['minecraft:item']['components']
 assert unfinished['minecraft:max_stack_size']==64 and unfinished['minecraft:allow_off_hand'] is True
 assert secret['minecraft:max_stack_size']==64 and secret['minecraft:food']['nutrition']==0 and secret['minecraft:food']['saturation_modifier']==0.0
 tex=load(RP/'textures/item_texture.json')['texture_data']
 assert tex['unfinished_skewer']['textures']=='textures/items/unfinished_skewer'
 assert tex['secret_skewer']['textures']=='textures/items/secret_skewer'
 assert (RP/'textures/items/unfinished_skewer.png').is_file() and (RP/'textures/items/secret_skewer.png').is_file()
 for name in ('a24_skewering_core.js','a23_hot_runtime.js','a23_oil_world.js'):assert (BP/'scripts'/name).is_file(),name
 runtime=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  'appendOutcome','threadCurrent','disassembleOff','SECRET_COOKED_INGREDIENTS_KEY','dynamicFood',
  'VANILLA_SMOKED','secretRemainders','FLUID_CAPACITY','cookeryOilType','playerInteractWithEntity'
 ):assert token in runtime,token
 assert "Object.hasOwn(RAW_TO_COOKED,id)||(id===SECRET_ID" in runtime
 assert "stack.setLore(lore);stack.setDynamicProperty(HOT_UNTIL_KEY,until)" in runtime
 hot=(BP/'scripts/a23_hot_runtime.js').read_text(encoding='utf-8')
 assert hot.index('stack.setLore(lore);')<hot.index('stack.setDynamicProperty(HOT,bucket(t+remaining))')
 oil=(BP/'scripts/a23_oil_world.js').read_text(encoding='utf-8')
 for token in ('FLUID_CAPACITY','OIL_BUCKET_POINTS',"item?.typeId===COOKERY_FILLED","current+OIL_BUCKET_POINTS>FLUID_CAPACITY"):assert token in oil,token
 core=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 for token in ('FAT_CAPACITY=256','FLUID_CAPACITY=64','OIL_BUCKET_POINTS=8','secretFood','raw_golden_skewer','ordinary_skewer'):assert token in core,token
 for p in BP.glob('scripts/*.js'):subprocess.run(['node','--check',str(p)],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a24_core.mjs')],check=True)
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
 result={
  'version':'A2.4.0','formal_foods':42,'configured_skewer_recipes':20,'hand_threading':True,
  'secret_dynamic_food':True,'raw_disassembly':True,'typed_oil_capacity':64,'fat_capacity':256,
  'bucket_points':8,'can_always_eat':True,'server_module':'2.9.0','compiled':a.compiled,
  'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a24-dash-verification.json' if a.compiled else 'a24-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
