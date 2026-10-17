from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
TEX_SHA='6b9a7d3f3b153ab42c0f725abc34b4b56003c5e1'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,9] and rm['header']['version']==[2,7,9]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.9 Beef Board Override BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.9 Beef Board Override RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 item=load(BP/'items/beef_chunks.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:beef_chunks'
 assert c['minecraft:max_stack_size']==64 and 'minecraft:food' not in c
 assert c['minecraft:icon']['textures']['default']=='beef_chunks'
 tex=RP/'textures/items/beef_chunks.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 atlas=load(RP/'textures/item_texture.json')['texture_data'];assert atlas['beef_chunks']['textures']=='textures/items/beef_chunks'

 core=(BP/'scripts/a279_beef_board_core.js').read_text(encoding='utf-8')
 for token in ("BEEF_ID='minecraft:beef'","COOKERY_OFFAL_ID='kaleidoscope_cookery:raw_cow_offal'","BEEF_CHUNKS_ID='kaleidoscope_grilling:beef_chunks'","CUTS=4","OUTPUT_COUNT=2","kc_station:"):assert token in core,token
 runtime=(BP/'scripts/a279_beef_board_runtime.js').read_text(encoding='utf-8')
 for token in ('tryScheduleBeefBoardOverride','world.getDynamicProperty','world.setDynamicProperty','system.run','board_model',"GameMode.Creative",'transaction rolled back'):assert token in runtime,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';" in main
 assert "if(tryScheduleBeefBoardOverride(e))return;" in main

 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 assert 'raw_beef_skewer' in a24 and a24.count('kaleidoscope_grilling:beef_chunks')>=2

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a279_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a279_runtime.mjs')],check=True)
 for test in ('test_a278_core.mjs','test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a279-parity.json')
 assert report['version']=='A2.7.9'
 assert report['java_recipe']=={'recipe_namespace':'kaleidoscope_cookery','input':'minecraft:beef','cuts':4,'model_id':'kaleidoscope_cookery:raw_cow_offal','result':'kaleidoscope_grilling:beef_chunks','count':2}
 assert report['cookery_bedrock']['native_beef_board_model']==0
 assert report['cookery_bedrock']['cookery_private_scripts_modified'] is False
 assert report['visual_parity']['bedrock_reuses_cookery_native_beef_model'] is True
 assert report['visual_parity']['engine_rendering_verified'] is False
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
  'version':'A2.7.9','beef_chunks_item':True,'beef_chopping_override':True,
  'cuts':4,'output_count':2,'cookery_native_model_0_reused':True,
  'cookery_private_scripts_modified':False,'transaction_rollback':True,'stale_hand_guard':True,
  'a278_chopping_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a279-dash-verification.json' if a.compiled else 'a279-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
