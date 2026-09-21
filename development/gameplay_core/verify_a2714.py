from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
TEX={'stage0':'228a95ee694f75f6f2770f74fb3b85acf044d92a','stage1':'5a0dda7aa376f96e42e8c20b7b3eb53bc1164592','stage2':'fdfa5a086de21aa2a437f1b2838e8c5a8efe473e','stage3':'1c587cbab8282e3b883f1534eab91bf226a10385','stage4':'5b9c4285c8fc3b23ea3cd5a431935955776f1471','stage5':'40ed161b56ce21c80e4d9b61c68aba1c4f3a616c','stage5_2':'c37ba99aa43123a0393f06c10f0cbe91e74c7056','stage6':'e8865cf66b83766df45123fe13ea81d5cc49149b','stage6_2':'64db168e8dd090b0310ebabaee2d043b64fb9615','stage7':'dc69075167f3a1f7807a0a9aeca7f1753756662f','stage7_2':'9345181aea1ed704ba56ca2b4e299674b9129804'}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,14] and rm['header']['version']==[2,7,14]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.14 Houttuynia Crop BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.14 Houttuynia Crop RP'

 item=load(BP/'items/houttuynia.json')['minecraft:item'];c=item['components']
 assert c['minecraft:block_placer']=={'block':'kaleidoscope_grilling:houttuynia_crop','use_on':['minecraft:farmland','minecraft:soul_sand'],'replace_block_item':False}
 assert c['minecraft:use_modifiers']['start_using']=='if_first'
 assert c['minecraft:food']['nutrition']==2 and c['minecraft:food']['saturation_modifier']==0.2

 block=load(BP/'blocks/houttuynia_crop.json')['minecraft:block'];d=block['description'];bc=block['components']
 assert d['identifier']=='kaleidoscope_grilling:houttuynia_crop'
 assert d['states']['kaleidoscope_grilling:age']==list(range(8))
 assert d['states']['kaleidoscope_grilling:red_variant']==[False,True]
 assert bc['kaleidoscope_grilling:houttuynia_crop_logic']=={}
 assert bc['minecraft:collision_box'] is False
 assert bc['minecraft:light_dampening']==0
 assert bc['minecraft:placement_filter']['conditions'][0]['block_filter']==['minecraft:farmland','minecraft:soul_sand']
 assert bc['minecraft:loot']=='loot_tables/blocks/houttuynia_crop.json'
 assert len(block['permutations'])==11
 mature=[x for x in block['permutations'] if "age') == 7" in x['condition']]
 assert len(mature)==2 and all(x['components']['minecraft:loot']=='loot_tables/blocks/houttuynia_crop_mature.json' for x in mature)

 geo=load(RP/'models/blocks/houttuynia_crop.geo.json')['minecraft:geometry'][0]
 assert geo['description']['identifier']=='geometry.kaleidoscope_grilling.houttuynia_crop'
 assert len(geo['bones'][0]['cubes'])==2
 atlas=load(RP/'textures/terrain_texture.json')['texture_data']
 for name,sha in TEX.items():
  p=RP/f'textures/blocks/crop/houttuynia/{name}.png';assert p.is_file() and blob(p)==sha,(name,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(name,im.size)
  assert atlas['houttuynia_'+name]['textures']==f'textures/blocks/crop/houttuynia/{name}'

 immature=load(BP/'loot_tables/blocks/houttuynia_crop.json');mature=load(BP/'loot_tables/blocks/houttuynia_crop_mature.json')
 assert immature['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:houttuynia'
 assert mature['pools'][0]['entries'][0]['functions'][0]['count']==2
 assert len(mature['pools'])==5
 assert abs(mature['pools'][1]['conditions'][0]['chance']-4/7)<1e-12
 for level in (1,2,3):
  cond=mature['pools'][level+1]['conditions'];assert cond[1]['condition']=='match_tool';assert cond[1]['enchantments'][0]['enchantment']=='fortune';assert cond[1]['enchantments'][0]['levels']['range_min']==level

 core=(BP/'scripts/a2714_houttuynia_crop_core.js').read_text(encoding='utf-8')
 runtime=(BP/'scripts/a2714_houttuynia_crop_runtime.js').read_text(encoding='utf-8')
 for token in ("MAX_AGE=7","RED_PLACEMENT_CHANCE=0.3","FARMLAND_MIN_SURVIVAL_LIGHT=8","MIN_GROWTH_LIGHT=9",'javaCropGrowthSpeed','bonemealAgeIncrease','wartAgeToCropAge'):assert token in core,token
 for token in ('system.beforeEvents.startup.subscribe','registerCustomComponent(COMPONENT_ID','beforeOnPlayerPlace','onRandomTick','onPlayerInteract','getLightLevel','GameMode.Creative','matureBonusCount'):assert token in runtime,token
 assert 'runInterval' not in runtime
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2713_houttuynia_processing_runtime.js';" in main and "import './a2714_houttuynia_crop_runtime.js';" in main

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2714_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2714_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2713_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2713_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2712_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2712_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2711_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2711_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2710_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2710_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2714-parity.json')
 assert report['version']=='A2.7.14' and report['crop']['max_age']==7
 assert report['crop']['soul_sand_forces_red'] is True and report['crop']['farmland_red_placement_chance']==0.3
 assert report['crop']['bonemeal_age_increase']==[2,5]
 assert report['drops']['overleveled_fortune_exact'] is False
 assert report['fortress_acquisition']['exact_structure_bounded_replacement'] is False
 assert report['survival_houttuynia_acquisition_complete'] is False
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

 result={'version':'A2.7.14','houttuynia_crop':True,'ages':8,'red_variant':True,'bonemeal':True,'java_growth_speed':True,'mature_fortune_0_3_exact':True,'fortress_world_acquisition_complete':False,'a2713_processing_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2714-dash-verification.json' if a.compiled else 'a2714-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
