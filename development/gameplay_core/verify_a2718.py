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
 assert bm['header']['version']==[2,7,18] and rm['header']['version']==[2,7,18]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.18 Onion Processing BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.18 Onion Processing RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 onion=load(BP/'items/onion.json')['minecraft:item'];oc=onion['components']
 assert onion['description']['identifier']=='kaleidoscope_grilling:onion'
 assert oc['minecraft:block_placer']['block']=='kaleidoscope_grilling:onion_crop'
 assert oc['minecraft:compostable']['composting_chance']==65
 powder=load(BP/'items/onion_powder.json')['minecraft:item'];pc=powder['components']
 assert powder['description']['identifier']=='kaleidoscope_grilling:onion_powder'
 assert pc['minecraft:max_stack_size']==64 and 'minecraft:food' not in pc

 core=(BP/'scripts/a2718_onion_processing_core.js').read_text(encoding='utf-8')
 for token in (
  "KC_API=1","ONION_ID='kaleidoscope_grilling:onion'",
  "ONION_POWDER_ID='kaleidoscope_grilling:onion_powder'",
  "kind:'millstone'","id:'kaleidoscope_grilling:millstone/onion_powder'",
  'count:1,chance:1.0'
 ):assert token in core,token
 runtime=(BP/'scripts/a2718_onion_processing_runtime.js').read_text(encoding='utf-8')
 for token in ('KC_READY_EVENT','KC_REGISTER_EVENT','registrationsForReady','sendScriptEvent'):assert token in runtime,token
 assert 'api_ping' not in runtime and 'KC_PING_EVENT' not in runtime

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2717_onion_crop_runtime.js';" in main
 assert "import './a2718_onion_processing_runtime.js';" in main

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2718_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2718_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2717_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2717_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2716_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2716_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2715_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2715_runtime.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2718-parity.json')
 assert report['version']=='A2.7.18'
 assert report['java_recipe']['tag_chain']==['#c:crops/onion','kaleidoscope_grilling:onion']
 assert report['java_recipe']['locked_baseline_resolved_inputs']==['kaleidoscope_grilling:onion']
 assert report['java_recipe']['count']==1 and report['java_recipe']['chance']==1.0
 assert report['cookery_bedrock']['extension_api']==1
 assert report['cookery_bedrock']['additional_api_ping'] is False
 assert report['cookery_bedrock']['private_scripts_modified'] is False
 assert report['common_tag_compatibility']['java_common_tag_extensible'] is True
 assert report['common_tag_compatibility']['bedrock_third_party_common_tag_expansion'] is False
 assert report['common_tag_compatibility']['locked_baseline_native_input_exact'] is True
 assert report['chain']['survival_onion_processing_chain_complete'] is True
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
  'version':'A2.7.18','onion_millstone_registered':True,'output_count':1,'output_chance':1.0,
  'additional_api_ping':False,'locked_baseline_onion_input_exact':True,
  'third_party_common_tag_expansion':False,'survival_onion_processing_chain_complete':True,
  'a2717_onion_crop_preserved':True,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2718-dash-verification.json' if a.compiled else 'a2718-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
