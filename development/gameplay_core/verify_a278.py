from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
EXPECTED={
 'carrot_dice':'c5359f186611411d51f1fe55077357d2c16efa61',
 'potato_slice':'9562676753ad5e32ea0e1345236e314ad4767b85'
}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,8] and rm['header']['version']==[2,7,8]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.8 Basic Chopping I BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.8 Basic Chopping I RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 tex=load(RP/'textures/item_texture.json')['texture_data']
 for id,sha in EXPECTED.items():
  item=load(BP/f'items/{id}.json')['minecraft:item'];c=item['components']
  assert item['description']['identifier']=='kaleidoscope_grilling:'+id
  assert c['minecraft:max_stack_size']==64
  assert 'minecraft:food' not in c
  assert c['minecraft:icon']['textures']['default']==id
  p=RP/f'textures/items/{id}.png';assert p.is_file()
  assert blob(p)==sha,(id,blob(p),sha)
  with Image.open(p) as im:assert im.size==(16,16),(id,im.size)
  assert tex[id]['textures']==f'textures/items/{id}'

 core=(BP/'scripts/a278_basic_chopping_core.js').read_text(encoding='utf-8')
 for token in ("input:'minecraft:carrot'","result:CARROT_DICE_ID,count:3,cuts:CUTS","input:'minecraft:potato'","result:POTATO_SLICE_ID,count:3,cuts:CUTS","CUTS=4","capabilities)?info.capabilities"):assert token in core,token
 runtime=(BP/'scripts/a278_basic_chopping_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','registrationsForReady','sendScriptEvent'):assert token in runtime,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8');assert "import './a278_basic_chopping_runtime.js';" in main

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a278_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for test in ('test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a278-parity.json')
 assert report['version']=='A2.7.8'
 assert report['recipes']['carrot_dice']['count']==3 and report['recipes']['carrot_dice']['cuts']==4
 assert report['recipes']['potato_slice']['count']==3 and report['recipes']['potato_slice']['cuts']==4
 assert report['explicitly_deferred_conflict']['beef_chunks']['planned_slice']=='A2.7.9'
 assert report['visual_difference']['exact_java_staged_board_visual'] is False
 assert report['cookery_bedrock']['lookup_priority_observed']=='BOARD_RECIPES[input] || getExtensionBoardRecipe(input)'
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
  'version':'A2.7.8','carrot_dice_item':True,'potato_slice_item':True,
  'carrot_chopping_registered':True,'potato_chopping_registered':True,
  'cuts':4,'beef_chunks_deferred_due_builtin_priority':True,
  'exact_java_staged_board_visual':False,
  'a277_transactions_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a278-dash-verification.json' if a.compiled else 'a278-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
