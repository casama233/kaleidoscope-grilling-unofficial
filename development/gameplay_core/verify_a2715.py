from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
SEED_SHA='89a7008164006a16dcd194ce27b6e5c165b14987'
TEX={
 'stage0':'afc9eb650ca70bece3a5f0fb08e979d64512e71c','stage1':'f4fa3cc14f2876aaf932dce2ebf7c4bd1a149aae',
 'stage2':'18ec9e2d1e55e491c90dbeb6c20d7ed652d0474e','stage3':'4cb6afb9df1d62f590f7cea118f88049cbdfef0c',
 'stage4':'4cb6afb9df1d62f590f7cea118f88049cbdfef0c','stage5':'314dcd4e949c5f610b1d07431424ec278ece5dc2',
 'stage6':'314dcd4e949c5f610b1d07431424ec278ece5dc2','stage7':'5f7f96c41be52be77d53a2e337e7b2dbfa9f7218'
}
P_BONUS=0.5714286

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,15] and rm['header']['version']==[2,7,15]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.15 Canola Crop BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.15 Canola Crop RP'

 item=load(BP/'items/canola_seeds.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:canola_seeds'
 assert c['minecraft:max_stack_size']==64
 assert c['minecraft:block_placer']=={'block':'kaleidoscope_grilling:canola_crop','use_on':['minecraft:farmland'],'replace_block_item':False}
 assert c['minecraft:compostable']=={'composting_chance':30}
 assert 'minecraft:food' not in c
 seed=RP/'textures/items/canola_seeds.png';assert seed.is_file() and blob(seed)==SEED_SHA
 with Image.open(seed) as im:assert im.size==(16,16)
 assert load(RP/'textures/item_texture.json')['texture_data']['canola_seeds']['textures']=='textures/items/canola_seeds'

 block=load(BP/'blocks/canola_crop.json')['minecraft:block'];d=block['description'];bc=block['components']
 assert d['identifier']=='kaleidoscope_grilling:canola_crop'
 assert d['states']['kaleidoscope_grilling:age']==list(range(8))
 assert len(block['permutations'])==8
 assert bc['minecraft:geometry']=='geometry.kaleidoscope_grilling.canola_crop'
 assert bc['minecraft:collision_box'] is False and bc['minecraft:light_dampening']==0
 assert bc['minecraft:placement_filter']['conditions'][0]['block_filter']==['minecraft:farmland']
 assert bc['kaleidoscope_grilling:canola_crop_logic']=={}
 assert block['permutations'][7]['components']['minecraft:loot']=='loot_tables/blocks/canola_crop_mature.json'

 geo=load(RP/'models/blocks/canola_crop.geo.json')['minecraft:geometry'][0]
 gd=geo['description'];assert gd['identifier']=='geometry.kaleidoscope_grilling.canola_crop'
 assert gd['texture_width']==16 and gd['texture_height']==28
 cubes=geo['bones'][0]['cubes'];assert len(cubes)==2
 for cube in cubes:
  assert cube['size']==[16,16,0]
  assert cube['uv']['north']=={'uv':[0,0],'uv_size':[16,28]}
  assert cube['uv']['south']=={'uv':[0,0],'uv_size':[16,28]}

 terrain=load(RP/'textures/terrain_texture.json')['texture_data']
 for name,sha in TEX.items():
  p=RP/f'textures/blocks/crop/canola/{name}.png';assert p.is_file() and blob(p)==sha,(name,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,28),(name,im.size)
  assert terrain['canola_'+name]['textures']==f'textures/blocks/crop/canola/{name}'

 immature=load(BP/'loot_tables/blocks/canola_crop.json');mature=load(BP/'loot_tables/blocks/canola_crop_mature.json')
 assert immature['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:canola_seeds'
 assert mature['pools'][0]['entries'][0]['functions'][0]['count']==2
 assert len(mature['pools'])==6
 assert mature['pools'][1]['conditions'][0]['chance']==P_BONUS and mature['pools'][2]['conditions'][0]['chance']==P_BONUS
 for level in (1,2,3):
  cond=mature['pools'][level+2]['conditions'];assert cond[0]['chance']==P_BONUS
  assert cond[1]['condition']=='match_tool';assert cond[1]['enchantments'][0]['enchantment']=='fortune';assert cond[1]['enchantments'][0]['levels']['range_min']==level

 core=(BP/'scripts/a2715_canola_crop_core.js').read_text(encoding='utf-8')
 runtime=(BP/'scripts/a2715_canola_crop_runtime.js').read_text(encoding='utf-8')
 for token in ("ACQUISITION_CHANCE=0.125","MATURE_BONUS_PROBABILITY=0.5714286","COMPOST_CHANCE=30",'acquisitionSeedCount','matureCanolaCount'):assert token in core,token
 for token in ('world.afterEvents.playerBreakBlock.subscribe',"minecraft:short_grass",'itemStackBeforeBreak','EquipmentSlot.Head','system.beforeEvents.startup.subscribe','registerCustomComponent(COMPONENT_ID'):assert token in runtime,token
 assert "from './a2714_houttuynia_crop_core.js'" in core
 assert 'runInterval' not in runtime
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2714_houttuynia_crop_runtime.js';" in main and "import './a2715_canola_crop_runtime.js';" in main

 assert (BP/'items/canola_powder.json').is_file()
 oil=load(BP/'recipes/oil_cake.json')['minecraft:recipe_shaped']
 assert oil['key']['P']['item']=='kaleidoscope_grilling:canola_powder' and oil['result']['item']=='kaleidoscope_grilling:oil_cake'
 assert not (BP/'scripts/a2715_canola_processing_runtime.js').exists()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2715_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2715_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2714_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2714_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2713_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2713_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2712_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2712_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2715-parity.json')
 assert report['version']=='A2.7.15'
 assert report['item']['composting_chance_percent']==30
 assert report['initial_acquisition']['chance']==0.125
 assert report['initial_acquisition']['required_head']==['kaleidoscope_cookery:straw_hat','kaleidoscope_cookery:straw_hat_flower']
 assert report['drops']['overleveled_fortune_exact'] is False
 assert report['survival_canola_seed_acquisition_complete'] is True
 assert report['survival_canola_oil_chain_complete'] is False
 assert report['downstream']['canola_seed_to_powder_processing_complete'] is False
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

 result={'version':'A2.7.15','canola_seed_item':True,'canola_crop':True,'ages':8,'straw_hat_acquisition':True,'compostable_30_percent':True,'mature_fortune_0_3_exact':True,'canola_seed_to_powder_processing_complete':False,'a2714_houttuynia_crop_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2715-dash-verification.json' if a.compiled else 'a2715-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
