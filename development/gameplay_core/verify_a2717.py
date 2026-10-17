from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
ITEM_SHA='103aa78661bf35aa6b3a42989a398573056faff1'
TEX={
 'stage0':'490cd255f3e94a82844e5c0dd4fbc0f39e7ed851','stage1':'27e70b8e92331894e46926a1a9acd19b77a7329d',
 'stage2':'22f7dd1f49602fce4cce32046bc2b70140b2cb7f','stage3':'8963fc4f952806dc0833eb19a4fbe1b831a3eb74',
 'stage4':'348515d3f3c59a5a06a4d366f831b676e71f16b4','stage5':'5a4631796be63179bcf796359eeba00a5986e04c',
 'stage6':'e8badfe410205c7d82745124cec24c5a93802208','stage7':'857cddb6802c9cf63f32d4ff799fd799beb753ff'
}
P_BONUS=0.5714286

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,17] and rm['header']['version']==[2,7,17]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.17 Onion Crop BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.17 Onion Crop RP'

 item=load(BP/'items/onion.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:onion'
 assert c['minecraft:max_stack_size']==64
 assert c['minecraft:block_placer']=={'block':'kaleidoscope_grilling:onion_crop','use_on':['minecraft:farmland'],'replace_block_item':False}
 assert c['minecraft:compostable']=={'composting_chance':65}
 assert 'minecraft:food' not in c
 onion=RP/'textures/items/onion.png';assert onion.is_file() and blob(onion)==ITEM_SHA
 with Image.open(onion) as im:assert im.size==(16,16)
 assert load(RP/'textures/item_texture.json')['texture_data']['onion']['textures']=='textures/items/onion'

 block=load(BP/'blocks/onion_crop.json')['minecraft:block'];d=block['description'];bc=block['components']
 assert d['identifier']=='kaleidoscope_grilling:onion_crop'
 assert d['states']['kaleidoscope_grilling:age']==list(range(8))
 assert len(block['permutations'])==8
 assert bc['minecraft:geometry']=='geometry.kaleidoscope_grilling.houttuynia_crop'
 assert bc['minecraft:collision_box'] is False and bc['minecraft:light_dampening']==0
 assert bc['minecraft:placement_filter']['conditions'][0]['block_filter']==['minecraft:farmland']
 assert bc['kaleidoscope_grilling:onion_crop_logic']=={}
 assert block['permutations'][7]['components']['minecraft:loot']=='loot_tables/blocks/onion_crop_mature.json'

 terrain=load(RP/'textures/terrain_texture.json')['texture_data']
 for name,sha in TEX.items():
  p=RP/f'textures/blocks/crop/onion/{name}.png';assert p.is_file() and blob(p)==sha,(name,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(name,im.size)
  assert terrain['onion_'+name]['textures']==f'textures/blocks/crop/onion/{name}'

 immature=load(BP/'loot_tables/blocks/onion_crop.json');mature=load(BP/'loot_tables/blocks/onion_crop_mature.json')
 assert immature['pools'][0]['entries'][0]['name']=='kaleidoscope_grilling:onion'
 assert mature['pools'][0]['entries'][0]['functions'][0]['count']==2
 assert len(mature['pools'])==6
 assert mature['pools'][1]['conditions'][0]['chance']==P_BONUS and mature['pools'][2]['conditions'][0]['chance']==P_BONUS
 for level in (1,2,3):
  cond=mature['pools'][level+2]['conditions'];assert cond[0]['chance']==P_BONUS
  assert cond[1]['condition']=='match_tool';assert cond[1]['enchantments'][0]['enchantment']=='fortune';assert cond[1]['enchantments'][0]['levels']['range_min']==level

 core=(BP/'scripts/a2717_onion_crop_core.js').read_text(encoding='utf-8')
 runtime=(BP/'scripts/a2717_onion_crop_runtime.js').read_text(encoding='utf-8')
 assert "from './a2715_canola_crop_core.js'" in core
 for token in ("COMPOST_CHANCE=65",'onionAcquisitionCount','matureOnionCount'):assert token in core,token
 for token in ('world.afterEvents.playerBreakBlock.subscribe',"minecraft:short_grass",'itemStackBeforeBreak','EquipmentSlot.Head','system.beforeEvents.startup.subscribe','registerCustomComponent(COMPONENT_ID'):assert token in runtime,token
 assert 'runInterval' not in runtime
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2716_canola_processing_runtime.js';" in main and "import './a2717_onion_crop_runtime.js';" in main

 assert (BP/'items/onion_powder.json').is_file()
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2717_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2717_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2716_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2716_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2715_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2715_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2714_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2714_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2717-parity.json')
 assert report['version']=='A2.7.17'
 assert report['item']['composting_chance_percent']==65
 assert report['initial_acquisition']['chance']==0.125
 assert report['initial_acquisition']['per_branch_probability_count_exact'] is True
 assert report['initial_acquisition']['full_java_rng_call_order_complete'] is False
 assert report['drops']['overleveled_fortune_exact'] is False
 assert report['survival_onion_acquisition_complete'] is True
 assert report['downstream']['onion_to_powder_processing_complete'] is False
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
  'version':'A2.7.17','onion_item':True,'onion_crop':True,'ages':8,'straw_hat_acquisition':True,
  'compostable_65_percent':True,'mature_fortune_0_3_exact':True,
  'onion_to_powder_processing_complete':False,'a2716_canola_chain_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2717-dash-verification.json' if a.compiled else 'a2717-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
