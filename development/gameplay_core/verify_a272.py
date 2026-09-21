from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git_blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,2] and rm['header']['version']==[2,7,2]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.2 Gameplay BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.2 Gameplay RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 item=load(BP/'items/sweet_potato.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:sweet_potato'
 assert c['minecraft:max_stack_size']==64 and c['minecraft:food']['nutrition']==3
 assert abs(c['minecraft:food']['saturation_modifier']-.1)<1e-9 and c['minecraft:food']['can_always_eat'] is False
 assert c['minecraft:use_animation']['value']=='eat'
 assert git_blob(RP/'textures/items/sweet_potato.png')=='6761c2d89d46df2e536dd6df3fe9fdb7c2262259'
 tex=load(RP/'textures/item_texture.json')['texture_data'];assert tex['sweet_potato']['textures']=='textures/items/sweet_potato'

 core=(BP/'scripts/a272_cookery_processing_core.js').read_text(encoding='utf-8')
 for token in ("KC_API=1","BOARD_CUTS=4","kind:'chopping_board'","kind:'millstone'","SWEET_POTATO_ID='kaleidoscope_grilling:sweet_potato'"):assert token in core,token
 rt=(BP/'scripts/a272_cookery_processing_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','recipesForReady','sendScriptEvent'):assert token in rt,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8');assert "import './a272_cookery_processing_runtime.js';" in main

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 for test in ('test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a272_runtime.mjs')],check=True)

 parity=load(P/'reports/a272-parity.json')
 assert parity['version']=='A2.7.2'
 assert parity['cookery_bedrock']['exact_public_archive_sha256']==COOKERY_SHA
 assert parity['cookery_bedrock']['extension_recipe_api']==1
 assert parity['recipes']['chopping_board']['cuts']==4 and parity['recipes']['chopping_board']['registered_through_public_api'] is True
 assert parity['recipes']['millstone']['count']==1 and parity['recipes']['millstone']['chance']==1.0
 assert parity['sweet_potato_item']['crop_planting_ported'] is False
 assert parity['java_audio_difference']['bedrock_public_api_stage_sound_hook'] is False
 assert parity['create_milling_ported'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.2','cookery_api':1,'cookery_exact_sha256':COOKERY_SHA,
  'sweet_potato_item':True,'chopping_board_registered':True,'board_cuts':4,'millstone_registered':True,
  'second_cut_java_sound_exact':False,'create_milling_ported':False,'crop_planting_ported':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a272-dash-verification.json' if a.compiled else 'a272-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
