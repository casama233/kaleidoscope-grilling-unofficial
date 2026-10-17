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
 assert bm['header']['version']==[2,7,5] and rm['header']['version']==[2,7,5]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.5 Grill Input Hardening BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.5 Grill Input Hardening RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 helper=(BP/'scripts/a275_grill_input_core.js').read_text(encoding='utf-8')
 for token in (
  'minecraft:wooden_shovel','minecraft:netherite_shovel',
  'kaleidoscope_cookery:kitchen_shovel','kaleidoscope_cookery:oiled_kitchen_shovel',
  'isInitialBlockPress','nextDurability'
 ):assert token in helper,token

 core=(BP/'scripts/core_logic.js').read_text(encoding='utf-8')
 brush_line=[x for x in core.splitlines() if "state.phase!==0||occupied<1" in x]
 assert len(brush_line)==1,brush_line
 assert '!state.lit' not in brush_line[0],brush_line[0]

 runtime=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  "import {isExtinguishTool,isInitialBlockPress,nextDurability} from './a275_grill_input_core.js';",
  "stack.getComponent('minecraft:durability')",
  'damageMainTool(player,1)',
  "if(isExtinguishTool(id)&&state.lit)",
  "state=light(state,false);writeState(block,state)",
  "if(!isInitialBlockPress(e.isFirstEvent))",
  "if(skewerInput){e.cancel=true;if(isInitialBlockPress(e.isFirstEvent))",
  "if(state.phase!==0||n<1){message(player,'§7現在不能刷油');return}"
 ):assert token in runtime,token

 # Ensure A2.7.4 exact Java GUI assets and A2.7.3 grill helper were not regressed.
 a274=load(P/'reports/a274-java-gui-icons.json')
 assert a274['exact_static_java_icons']==39 and len(a274['items'])==41
 assert (BP/'blocks/grill_legs.json').is_file()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a275_core.mjs')],check=True)
 for test in ('test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a275-grill-input-hardening.json')
 assert report['version']=='A2.7.5'
 assert report['fixes']['held_block_interaction_repeat']['status']=='fixed'
 assert report['fixes']['extinguish']['status']=='ported'
 assert report['fixes']['oil_before_ignition']['status']=='fixed'
 assert report['fixes']['flint_and_steel_durability']['status']=='fixed'
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
  'version':'A2.7.5',
  'repeat_block_input_suppressed':True,
  'java_shovel_extinguish_ported':True,
  'oil_before_ignition_allowed':True,
  'flint_and_steel_durability':True,
  'a274_java_icons_preserved':True,
  'a273_grill_helper_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a275-dash-verification.json' if a.compiled else 'a275-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
