from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
TEX_SHA='60aab20cf2c9c4b250780430f7114c22ae7b9dff'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,12] and rm['header']['version']==[2,7,12]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.12 Remaining Knife Drops BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.12 Remaining Knife Drops RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 item=load(BP/'items/squid_tentacle.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:squid_tentacle'
 assert c['minecraft:max_stack_size']==64 and 'minecraft:food' not in c
 assert c['minecraft:icon']['textures']['default']=='squid_tentacle'
 tex=RP/'textures/items/squid_tentacle.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 atlas=load(RP/'textures/item_texture.json')['texture_data'];assert atlas['squid_tentacle']['textures']=='textures/items/squid_tentacle'

 core=(BP/'scripts/a2712_remaining_knife_drops_core.js').read_text(encoding='utf-8')
 for token in (
  "COW_ID='minecraft:cow'","SQUID_ID='minecraft:squid'",
  "RAW_COW_OFFAL_ID='kaleidoscope_cookery:raw_cow_offal'",
  "SQUID_TENTACLE_ID='kaleidoscope_grilling:squid_tentacle'",
  'SQUID_DROP_CHANCE=0.5','cowOffalDropCount','squidTentacleDropCount','squidTentacleShouldDrop'
 ):assert token in core,token
 runtime=(BP/'scripts/a2712_remaining_knife_drops_runtime.js').read_text(encoding='utf-8')
 for token in (
  "from './a2710_chicken_acquisition_core.js'",
  'world.afterEvents.entityDie.subscribe',
  "killer?.typeId!=='minecraft:player'",
  'isKitchenKnife(weapon?.typeId)',
  'spawn(dead,RAW_COW_OFFAL_ID',
  'spawn(dead,SQUID_TENTACLE_ID'
 ):assert token in runtime,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2710_chicken_acquisition_runtime.js';" in main
 assert "import './a2711_mantou_chopping_runtime.js';" in main
 assert "import './a2712_remaining_knife_drops_runtime.js';" in main

 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 assert 'raw_squid_tentacle_skewer' in a24 and a24.count('kaleidoscope_grilling:squid_tentacle')>=3

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2712_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2712_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2711_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2711_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2710_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2710_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a279_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a279_runtime.mjs')],check=True)
 for test in ('test_a278_core.mjs','test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2712-parity.json')
 assert report['version']=='A2.7.12'
 assert report['drops']['cow']['chance']==1.0
 assert report['drops']['cow']['base_count']=='1 + random(0..1)'
 assert report['drops']['squid']['chance']==0.5
 assert report['drops']['squid']['base_count']=='2 + random(0..1)'
 assert report['items']['squid_tentacle']['max_stack_size']==64
 assert report['cookery_bedrock']['private_scripts_modified'] is False
 assert report['downstream']['squid_fixed_skewer_chain_reachable'] is True
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
  'version':'A2.7.12',
  'cow_raw_offal_knife_drop':True,'squid_tentacle_item':True,'squid_tentacle_knife_drop':True,
  'cow_base_count_range':[1,2],'squid_base_count_range':[2,3],'squid_chance':0.5,
  'looting_bonus_inclusive':True,'a2710_chicken_acquisition_preserved':True,
  'a2711_mantou_chopping_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2712-dash-verification.json' if a.compiled else 'a2712-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
