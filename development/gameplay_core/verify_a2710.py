from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
TEX_SHA='c89c916e0611d7de9d821e122b2d88c099809cbf'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,10] and rm['header']['version']==[2,7,10]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.10 Mantou Chopping BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.10 Mantou Chopping RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 item=load(BP/'items/raw_mantou_slice.json')['minecraft:item'];c=item['components']
 assert item['description']['identifier']=='kaleidoscope_grilling:raw_mantou_slice'
 assert c['minecraft:max_stack_size']==64 and 'minecraft:food' not in c
 assert c['minecraft:icon']['textures']['default']=='raw_mantou_slice'
 tex=RP/'textures/items/raw_mantou_slice.png';assert tex.is_file() and blob(tex)==TEX_SHA
 with Image.open(tex) as im:assert im.size==(16,16)
 atlas=load(RP/'textures/item_texture.json')['texture_data'];assert atlas['raw_mantou_slice']['textures']=='textures/items/raw_mantou_slice'

 core=(BP/'scripts/a2710_mantou_chopping_core.js').read_text(encoding='utf-8')
 for token in (
  "MANTOU_ID='kaleidoscope_cookery:mantou'",
  "RAW_MANTOU_SLICE_ID='kaleidoscope_grilling:raw_mantou_slice'",
  'CUTS=4','OUTPUT_COUNT=3',"kind:'chopping_board'",
  "id:'kaleidoscope_grilling:chopping_board/raw_mantou_slice'"
 ):assert token in core,token
 runtime=(BP/'scripts/a2710_mantou_chopping_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','registrationsForReady','sendScriptEvent'):assert token in runtime,token
 assert 'KC_PING_EVENT' not in runtime
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a278_basic_chopping_runtime.js';" in main
 assert "import './a2710_mantou_chopping_runtime.js';" in main
 a24=(BP/'scripts/a24_skewering_core.js').read_text(encoding='utf-8')
 assert 'raw_bun_slice_skewer' in a24 and a24.count('kaleidoscope_grilling:raw_mantou_slice')>=3

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2710_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2710_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a279_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a279_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a278_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a278_runtime.mjs')],check=True)
 for test in ('test_a277_core.mjs','test_a276_core.mjs','test_a275_core.mjs','test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2710-parity.json')
 assert report['version']=='A2.7.10'
 assert report['java_recipe']=={
  'id':'kaleidoscope_grilling:chopping_board/raw_mantou_slice',
  'input':'kaleidoscope_cookery:mantou','cuts':4,
  'model_id':'kaleidoscope_grilling:raw_mantou_slice',
  'result':'kaleidoscope_grilling:raw_mantou_slice','count':3
 }
 assert report['cookery_bedrock']['built_in_mantou_board_recipe'] is False
 assert report['downstream']['required_raw_mantou_slices']==3
 assert report['downstream']['mantou_to_fixed_bun_skewer_chain_reachable'] is True
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
  'version':'A2.7.10','raw_mantou_slice_item':True,'mantou_chopping_registered':True,
  'cuts':4,'output_count':3,'bun_slice_chain_reachable':True,
  'exact_java_staged_board_visual':False,
  'a279_beef_override_preserved':True,'a278_basic_chopping_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2710-dash-verification.json' if a.compiled else 'a2710-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
