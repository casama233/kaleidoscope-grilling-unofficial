from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
EXPECTED={
 'chicken_skin':'5a8517468ed9da877b219047e1032d3a4c728bfc',
 'chicken_wing':'4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71'
}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,10] and rm['header']['version']==[2,7,10]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.10 Chicken Acquisition BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.10 Chicken Acquisition RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 atlas=load(RP/'textures/item_texture.json')['texture_data']
 for id,sha in EXPECTED.items():
  p=RP/f'textures/items/{id}.png';assert p.is_file() and blob(p)==sha,(id,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(id,im.size)
  assert atlas[id]['textures']==f'textures/items/{id}'

 skin=load(BP/'items/chicken_skin.json')['minecraft:item'];sc=skin['components']
 assert skin['description']['identifier']=='kaleidoscope_grilling:chicken_skin'
 assert sc['minecraft:max_stack_size']==64 and 'minecraft:food' not in sc

 wing=load(BP/'items/chicken_wing.json')['minecraft:item'];wc=wing['components']
 assert wing['description']['identifier']=='kaleidoscope_grilling:chicken_wing'
 assert wc['minecraft:max_stack_size']==64 and wc['minecraft:allow_off_hand'] is True
 assert wc['minecraft:food']=={'can_always_eat':False,'nutrition':2,'saturation_modifier':0.06}
 assert wc['minecraft:use_modifiers']['use_duration']==1.6
 assert wc['minecraft:use_animation']['value']=='eat'
 assert 'minecraft:is_food' in wc['minecraft:tags']['tags']

 core=(BP/'scripts/a2710_chicken_acquisition_core.js').read_text(encoding='utf-8')
 for token in (
  "CHICKEN_SKIN_ID='kaleidoscope_grilling:chicken_skin'",
  "CHICKEN_WING_ID='kaleidoscope_grilling:chicken_wing'",
  "RAW_SMALL_MEATS_ID='kaleidoscope_cookery:raw_cut_small_meats'",
  'chickenSkinCompletionCandidate','chickenBoardCompletionCommitted','chickenSkinDropCount','chickenWingDropCount'
 ):assert token in core,token

 runtime=(BP/'scripts/a2710_chicken_acquisition_runtime.js').read_text(encoding='utf-8')
 for token in (
  'world.beforeEvents.playerInteractWithBlock.subscribe',
  'world.afterEvents.entityDie.subscribe',
  'PENDING_SKIN',
  "getEnchantment('looting')",
  'dead?.typeId!==CHICKEN_ID',
  "killer?.typeId!=='minecraft:player'",
  'spawnItem(new ItemStack(CHICKEN_WING_ID,count)'
 ):assert token in runtime,token
 assert 'damagingProjectile' not in runtime

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2710_chicken_acquisition_runtime.js';" in main

 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 assert a24.count('kaleidoscope_grilling:chicken_skin')>=2
 assert a24.count('kaleidoscope_grilling:chicken_wing')>=2

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2710_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2710_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a279_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a279_runtime.mjs')],check=True)
 for test in ('test_a278_core.mjs','test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2710-parity.json')
 assert report['version']=='A2.7.10'
 assert report['items']['chicken_wing']['nutrition']==2 and report['items']['chicken_wing']['saturation_modifier']==0.06
 assert report['chicken_skin']['java_extra_drop'].endswith('chicken_skin x(1..3)')
 assert report['chicken_wing']['chance']==1.0
 assert report['chicken_wing']['projectile_note'].startswith('no explicit projectile rejection')
 assert report['cookery_bedrock']['chicken_board_model']==2
 assert report['cookery_bedrock']['private_scripts_modified'] is False
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
  'version':'A2.7.10',
  'chicken_skin_item':True,'chicken_wing_item':True,
  'chicken_skin_board_bonus':True,'chicken_wing_knife_kill_drop':True,
  'skin_count_range':[1,3],'wing_base_count_range':[1,2],'looting_bonus_inclusive':True,
  'cookery_output_preserved':'kaleidoscope_cookery:raw_cut_small_meats x2',
  'cookery_private_scripts_modified':False,
  'a279_beef_override_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2710-dash-verification.json' if a.compiled else 'a2710-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
