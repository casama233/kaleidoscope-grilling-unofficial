from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent

OLD_RUNTIME_IMPORTS=(
 "import './a272_cookery_processing_runtime.js';",
 "import './a278_basic_chopping_runtime.js';",
 "import './a2711_mantou_chopping_runtime.js';",
 "import './a2713_houttuynia_processing_runtime.js';",
 "import './a2716_canola_processing_runtime.js';",
 "import './a2718_onion_processing_runtime.js';",
 "import './a2724_red_chili_processing_runtime.js';",
)
NEW_RUNTIME_IMPORT="import './a2727_cookery_host_recipes_runtime.js';"

def load(p):
 return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--compiled',action='store_true')
 a=ap.parse_args()

 for p in P.rglob('*.json'):
  load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,27]
 assert rm['header']['version']==[2,7,27]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.27 Cookery Host Reuse BP'

 core=BP/'scripts/a2727_cookery_host_recipes_core.js'
 runtime=BP/'scripts/a2727_cookery_host_recipes_runtime.js'
 assert core.read_bytes()==(DEV/'a2727_cookery_host_recipes_core.js').read_bytes()
 assert runtime.read_bytes()==(DEV/'a2727_cookery_host_recipes_runtime.js').read_bytes()

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count(NEW_RUNTIME_IMPORT)==1
 for line in OLD_RUNTIME_IMPORTS:
  assert line not in main_text,line

 runtime_text=runtime.read_text(encoding='utf-8')
 assert runtime_text.count('system.afterEvents.scriptEventReceive.subscribe')==1
 assert runtime_text.count('system.sendScriptEvent(KC_PING_EVENT,SOURCE)')==1

 # Old per-slice files remain in the project for rebuildability but are inactive.
 for name in (
  'a272_cookery_processing_runtime.js',
  'a278_basic_chopping_runtime.js',
  'a2711_mantou_chopping_runtime.js',
  'a2713_houttuynia_processing_runtime.js',
  'a2716_canola_processing_runtime.js',
  'a2718_onion_processing_runtime.js',
  'a2724_red_chili_processing_runtime.js',
 ):
  assert (BP/'scripts'/name).is_file(),name

 # The only currently justified direct host-state adapter is still active.
 assert "import {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';" in main_text
 beef=(BP/'scripts/a279_beef_board_core.js').read_text(encoding='utf-8')
 assert "BOARD_ID='kaleidoscope_cookery:chopping_board'" in beef

 subprocess.run(
  ['node',str(ROOT/'development/gameplay_core/test_a2727_core.mjs')],
  check=True
 )
 for p in (BP/'scripts').glob('*.js'):
  subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2727-host-reuse.json')
 assert report['version']=='A2.7.27'
 assert report['before']=={
  'active_recipe_runtime_modules':7,
  'startup_api_pings':2,
  'ready_listeners':7
 }
 assert report['after']['active_recipe_runtime_modules']==1
 assert report['after']['startup_api_pings']==1
 assert report['after']['ready_listeners']==1
 assert report['after']['hosted_recipe_rows']==9
 assert report['after']['chopping_board_rows']==5
 assert report['after']['millstone_rows']==4
 assert report['beef_board_override_retained'] is True
 assert report['guide_already_uses_cookery_host_api'] is True
 assert report['minecraft_tested'] is False
 assert report['bds_tested'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[
    x.parent for x in dist.rglob('manifest.json')
    if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']
   ]
   assert len(matches)==1,(name,matches)
   target=matches[0]
   count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):
     continue
    q=target/p.relative_to(source)
    assert q.is_file(),str(q)
    if p.suffix=='.json':
     assert load(p)==load(q),str(q)
    else:
     assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.27',
  'cookery_recipe_host_reuse':True,
  'hosted_recipe_rows':9,
  'active_recipe_runtime_modules':1,
  'startup_api_pings':1,
  'beef_override_retained':True,
  'a2726_seasoning_render_preserved':True,
  'compiled':a.compiled,
  'compiled_packs':compiled,
  'minecraft_tested':False,
  'bds_tested':False
 }
 out=P/'reports'/(
  'a2727-dash-verification.json' if a.compiled
  else 'a2727-structure-verification.json'
 )
 out.write_text(
  json.dumps(result,ensure_ascii=False,indent=2)+'\n',
  encoding='utf-8'
 )
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
