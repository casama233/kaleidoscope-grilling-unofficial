from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,16] and rm['header']['version']==[2,7,16]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.16 Canola Processing BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.16 Canola Processing RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 seeds=load(BP/'items/canola_seeds.json')['minecraft:item']
 assert seeds['description']['identifier']=='kaleidoscope_grilling:canola_seeds'
 assert seeds['components']['minecraft:block_placer']['block']=='kaleidoscope_grilling:canola_crop'
 powder=load(BP/'items/canola_powder.json')['minecraft:item']
 assert powder['description']['identifier']=='kaleidoscope_grilling:canola_powder'
 assert powder['components']['minecraft:max_stack_size']==64 and 'minecraft:food' not in powder['components']

 core=(BP/'scripts/a2716_canola_processing_core.js').read_text(encoding='utf-8')
 for token in (
  "KC_API=1","CANOLA_SEEDS_ID='kaleidoscope_grilling:canola_seeds'",
  "CANOLA_POWDER_ID='kaleidoscope_grilling:canola_powder'",
  "kind:'millstone'","id:'kaleidoscope_grilling:millstone/canola_powder'",
  'count:1,chance:1.0'
 ):assert token in core,token
 runtime=(BP/'scripts/a2716_canola_processing_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','registrationsForReady','sendScriptEvent'):assert token in runtime,token
 assert 'api_ping' not in runtime and 'KC_PING_EVENT' not in runtime

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2715_canola_crop_runtime.js';" in main
 assert "import './a2716_canola_processing_runtime.js';" in main

 oil=load(BP/'recipes/oil_cake.json')['minecraft:recipe_shaped']
 assert oil['pattern']==['PPP','PWP','PPP']
 assert oil['key']['P']['item']=='kaleidoscope_grilling:canola_powder'
 assert oil['key']['W']['item']=='minecraft:wheat'
 assert oil['result']=={'item':'kaleidoscope_grilling:oil_cake','count':1}
 a26=(BP/'scripts/a26_oil_machine_core.js').read_text(encoding='utf-8')
 for token in (
  "OIL_CAKE_ID='kaleidoscope_grilling:oil_cake'",
  'PRESS_MAX_CAKES=4','PRESS_REQUIRED_PROGRESS=16','PRESS_OUTPUT_BUCKETS=4'
 ):assert token in a26,token

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2716_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2716_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2715_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2715_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2714_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2714_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2713_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2713_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a26_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2716-parity.json')
 assert report['version']=='A2.7.16'
 assert report['java_recipe']['tag_values']==['kaleidoscope_grilling:canola_seeds']
 assert report['java_recipe']['count']==1 and report['java_recipe']['chance']==1.0
 assert report['cookery_bedrock']['extension_api']==1
 assert report['cookery_bedrock']['additional_api_ping'] is False
 assert report['cookery_bedrock']['private_scripts_modified'] is False
 assert report['chain']['canola_oil_survival_chain_complete'] is True
 assert report['create_optional_processing']['bedrock_create_ported'] is False
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
  'version':'A2.7.16','canola_millstone_registered':True,'output_count':1,'output_chance':1.0,
  'additional_api_ping':False,'canola_oil_survival_chain_complete':True,
  'a2715_canola_crop_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2716-dash-verification.json' if a.compiled else 'a2716-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
