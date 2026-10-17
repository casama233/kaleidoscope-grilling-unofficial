from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
EXPECTED={'houttuynia':'40afc94ae7826ddb7cb5a8cd106434a6745dfe25','minced_houttuynia':'c6653c730bb5d1fefab02db05388b0f2e6aefc30'}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,13] and rm['header']['version']==[2,7,13]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.13 Houttuynia Processing BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.13 Houttuynia Processing RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 atlas=load(RP/'textures/item_texture.json')['texture_data']
 for id,sha in EXPECTED.items():
  p=RP/f'textures/items/{id}.png';assert p.is_file() and blob(p)==sha,(id,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(id,im.size)
  assert atlas[id]['textures']==f'textures/items/{id}'

 h=load(BP/'items/houttuynia.json')['minecraft:item'];hc=h['components']
 assert h['description']['identifier']=='kaleidoscope_grilling:houttuynia'
 assert hc['minecraft:max_stack_size']==64
 assert hc['minecraft:food']=={'can_always_eat':False,'nutrition':2,'saturation_modifier':0.2}
 assert hc['minecraft:use_animation']['value']=='eat'
 assert hc['minecraft:allow_off_hand'] is True
 assert 'minecraft:block_placer' not in hc

 m=load(BP/'items/minced_houttuynia.json')['minecraft:item'];mc=m['components']
 assert m['description']['identifier']=='kaleidoscope_grilling:minced_houttuynia'
 assert mc['minecraft:max_stack_size']==64 and 'minecraft:food' not in mc

 core=(BP/'scripts/a2713_houttuynia_processing_core.js').read_text(encoding='utf-8')
 for token in (
  "HOUTTUYNIA_ID='kaleidoscope_grilling:houttuynia'",
  "MINCED_HOUTTUYNIA_ID='kaleidoscope_grilling:minced_houttuynia'",
  'CUTS=4','OUTPUT_COUNT=1',
  "id:'kaleidoscope_grilling:chopping_board/minced_houttuynia'"
 ):assert token in core,token
 runtime=(BP/'scripts/a2713_houttuynia_processing_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','registrationsForReady','sendScriptEvent'):assert token in runtime,token
 assert 'KC_PING_EVENT' not in runtime

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2712_remaining_knife_drops_runtime.js';" in main
 assert "import './a2713_houttuynia_processing_runtime.js';" in main
 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 assert 'raw_slime_skewer' in a24 and 'kaleidoscope_grilling:houttuynia' in a24
 assert 'raw_sweet_potato_sheet_skewer' in a24 and a24.count('kaleidoscope_grilling:minced_houttuynia')>=2

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2713_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2713_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2712_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2712_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2711_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2711_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2710_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2710_runtime.mjs')],check=True)
 for test in ('test_a279_core.mjs','test_a278_core.mjs','test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a279_runtime.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2713-parity.json')
 assert report['version']=='A2.7.13'
 assert report['java_tag']['values']==['kaleidoscope_grilling:houttuynia']
 assert report['java_tag']['direct_item_registration_is_exact_for_locked_baseline'] is True
 assert report['java_recipe']['cuts']==4 and report['java_recipe']['count']==1
 assert report['items']['houttuynia']['nutrition']==2 and report['items']['houttuynia']['saturation_modifier']==0.2
 assert report['items']['houttuynia']['bedrock_crop_placer'] is False
 assert report['deferred_acquisition']['survival_houttuynia_acquisition_complete'] is False
 assert report['cookery_bedrock']['built_in_houttuynia_board_recipe'] is False
 assert report['visual_difference']['exact_java_staged_board_visual'] is False
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
  'version':'A2.7.13',
  'houttuynia_item':True,'minced_houttuynia_item':True,'houttuynia_chopping_registered':True,
  'cuts':4,'output_count':1,'survival_houttuynia_acquisition_complete':False,
  'fortress_chest_override_avoided':True,'crop_worldgen_deferred':True,
  'a2712_remaining_knife_drops_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2713-dash-verification.json' if a.compiled else 'a2713-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
