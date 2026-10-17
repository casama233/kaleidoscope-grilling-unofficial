from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
ITEM_SHA='6761c2d89d46df2e536dd6df3fe9fdb7c2262259'
TEX={
 'stage0':'608a3eefe99930634897aee339356fd4d87a3829','stage1':'22f4433daf385c206e6da0e4860c5877c3ddbb66',
 'stage2':'22f4433daf385c206e6da0e4860c5877c3ddbb66','stage3':'7b8349e033f88b4f5e79a55e258da8e38a1ccee7',
 'stage4':'7b8349e033f88b4f5e79a55e258da8e38a1ccee7','stage5':'bec26da1ffb404891263206e4918de9e80fa19a8',
 'stage6':'bec26da1ffb404891263206e4918de9e80fa19a8','stage7':'1c4f02073284ed2efb738bd69d090750a38ff75e'
}
P_BONUS=0.5714286

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,19] and rm['header']['version']==[2,7,19]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.19 Sweet Potato Crop BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.19 Sweet Potato Crop RP'

 item=load(BP/'items/sweet_potato.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:sweet_potato'
 assert c['minecraft:max_stack_size']==64 and c['minecraft:allow_off_hand'] is True
 assert c['minecraft:food']['nutrition']==3 and abs(c['minecraft:food']['saturation_modifier']-.1)<1e-9
 assert c['minecraft:food']['can_always_eat'] is False
 assert c['minecraft:use_modifiers']['start_using']=='if_first'
 assert c['minecraft:block_placer']=={'block':'kaleidoscope_grilling:sweet_potato_crop','use_on':['minecraft:farmland'],'replace_block_item':False}
 assert c['minecraft:compostable']=={'composting_chance':65}
 assert blob(RP/'textures/items/sweet_potato.png')==ITEM_SHA

 block=load(BP/'blocks/sweet_potato_crop.json')['minecraft:block'];d=block['description'];bc=block['components']
 assert d['identifier']=='kaleidoscope_grilling:sweet_potato_crop'
 assert d['states']['kaleidoscope_grilling:age']==list(range(8))
 assert len(block['permutations'])==8
 assert bc['minecraft:geometry']=='geometry.kaleidoscope_grilling.houttuynia_crop'
 assert bc['minecraft:collision_box'] is False and bc['minecraft:light_dampening']==0
 assert bc['minecraft:placement_filter']['conditions'][0]['block_filter']==['minecraft:farmland']
 assert bc['kaleidoscope_grilling:sweet_potato_crop_logic']=={}
 assert block['permutations'][7]['components']['minecraft:loot']=='loot_tables/blocks/sweet_potato_crop_mature.json'

 terrain=load(RP/'textures/terrain_texture.json')['texture_data']
 for name,sha in TEX.items():
  p=RP/f'textures/blocks/crop/sweet_potato/{name}.png';assert p.is_file() and blob(p)==sha,(name,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(name,im.size)
  assert terrain['sweet_potato_'+name]['textures']==f'textures/blocks/crop/sweet_potato/{name}'

 immature=load(BP/'loot_tables/blocks/sweet_potato_crop.json');mature=load(BP/'loot_tables/blocks/sweet_potato_crop_mature.json')
 assert immature['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:sweet_potato'
 assert mature['pools'][0]['entries'][0]['functions'][0]['count']==3
 assert len(mature['pools'])==7
 for i in (1,2,3):assert mature['pools'][i]['conditions'][0]['chance']==P_BONUS
 for level in (1,2,3):
  cond=mature['pools'][level+3]['conditions'];assert cond[0]['chance']==P_BONUS
  assert cond[1]['condition']=='match_tool';assert cond[1]['enchantments'][0]['enchantment']=='fortune';assert cond[1]['enchantments'][0]['levels']['range_min']==level

 core=(BP/'scripts/a2719_sweet_potato_crop_core.js').read_text(encoding='utf-8')
 runtime=(BP/'scripts/a2719_sweet_potato_crop_runtime.js').read_text(encoding='utf-8')
 for token in ("COMPOST_CHANCE=65","CROP_DROP_ORDER=Object.freeze([CANOLA_SEEDS_ID,SWEET_POTATO_ID,ONION_ID])",'matureSweetPotatoCount','cropDropPlan'):assert token in core,token
 for token in ('world.afterEvents.playerBreakBlock.subscribe',"minecraft:short_grass",'Array.from({length:6},()=>Math.random())','system.beforeEvents.startup.subscribe','registerCustomComponent(COMPONENT_ID'):assert token in runtime,token
 assert 'runInterval' not in runtime

 canola=(BP/'scripts/a2715_canola_crop_runtime.js').read_text(encoding='utf-8')
 onion=(BP/'scripts/a2717_onion_crop_runtime.js').read_text(encoding='utf-8')
 assert 'world.afterEvents.playerBreakBlock.subscribe' not in canola
 assert 'world.afterEvents.playerBreakBlock.subscribe' not in onion
 assert runtime.count('world.afterEvents.playerBreakBlock.subscribe')==1

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2718_onion_processing_runtime.js';" in main
 assert "import './a2719_sweet_potato_crop_runtime.js';" in main

 a272=(BP/'scripts/a272_cookery_processing_core.js').read_text(encoding='utf-8')
 for token in ("SWEET_POTATO_ID='kaleidoscope_grilling:sweet_potato'","kind:'millstone'","input:SWEET_POTATO_ID","id:POWDER_ID,count:1,chance:1.0"):assert token in a272,token
 a271=(BP/'scripts/a271_sweet_potato_core.js').read_text(encoding='utf-8')
 assert "POWDER_ID='kaleidoscope_grilling:sweet_potato_powder'" in a271

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2719_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2719_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2718_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2718_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2719-parity.json')
 assert report['version']=='A2.7.19'
 assert report['item']['composting_chance_percent']==65
 assert report['drops']['mature'].startswith('3 + Binomial(Fortune+3')
 assert report['initial_acquisition']['java_branch_order']==['kaleidoscope_grilling:canola_seeds','kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:onion']
 assert report['initial_acquisition']['single_unified_subscriber'] is True
 assert report['initial_acquisition']['java_branch_draw_order_complete'] is True
 assert report['initial_acquisition']['java_rng_algorithm_identical'] is False
 assert report['downstream']['survival_acquisition_and_processing_to_sheet_complete'] is True
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
  'version':'A2.7.19','sweet_potato_crop':True,'ages':8,'food_and_plantable':True,'compostable_65_percent':True,
  'mature_fortune_0_3_exact':True,'unified_cropdrop_handler':True,'java_branch_draw_order_complete':True,
  'java_rng_algorithm_identical':False,'sweet_potato_survival_processing_to_sheet_complete':True,
  'a2718_onion_processing_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2719-dash-verification.json' if a.compiled else 'a2719-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
