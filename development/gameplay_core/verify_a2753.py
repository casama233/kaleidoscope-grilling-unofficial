from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

LANG_KEYS=(
 'advancement.kaleidoscope_grilling.mountain_fragrance.title',
 'advancement.kaleidoscope_grilling.mountain_fragrance.description',
 'message.kaleidoscope_grilling.advancement.goal_announce',
 'message.kaleidoscope_grilling.advancement.goal_self',
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,53] and rm['header']['version']==[2,7,53]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.53 Mountain Fragrance Advancement BP'

 for name in ('a2753_advancement_core.js','a2753_advancement_runtime.js'):
  assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 core=(BP/'scripts/a2753_advancement_core.js').read_text(encoding='utf-8')
 for token in (
  "id:'mountain_fragrance'","parent:'human_fireworks'","frame:'goal'","xp:25",
  "propertyKey:ADVANCEMENT_PREFIX+'mountain_fragrance'","announce:true","showToast:true","hidden:false"
 ):assert token in core,token

 runtime=(BP/'scripts/a2753_advancement_runtime.js').read_text(encoding='utf-8')
 for token in (
  'awardOneShotAdvancement','getDynamicProperty','setDynamicProperty','addExperience',
  "runCommand('xp '+n+' @s')",'world.sendMessage','awardMountainFragrance'
 ):assert token in runtime,token
 assert 'runInterval' not in runtime
 assert '.subscribe(' not in runtime

 pepper=(BP/'scripts/a2748_pepper_tree_runtime.js').read_text(encoding='utf-8')
 assert pepper.count("import {awardMountainFragrance} from './a2753_advancement_runtime.js';")==1
 assert pepper.count('awardMountainFragrance(player);')==1
 harvest=pepper.index('drop(block,SICHUAN_PEPPER_ID,harvestedPepperCount(Math.random()));')
 award=pepper.index('awardMountainFragrance(player);',harvest)
 reset=pepper.index('setState(block,HAS_PEPPER_STATE,false);',award)
 assert harvest<award<reset
 break_start=pepper.index('function breakLeaves(')
 break_end=pepper.index('system.beforeEvents.startup.subscribe',break_start)
 assert 'awardMountainFragrance' not in pepper[break_start:break_end]

 # Preserve preceding content slices.
 for path in (
  BP/'features/pepper_tree_worldgen.json',
  BP/'feature_rules/pepper_tree_worldgen_rule.json',
  BP/'items/potato_beef_stew.json',
  BP/'items/red_sweet_potato_porridge.json',
  BP/'items/sour_spicy_noodles.json',
 ):assert path.is_file(),path

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2753_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2753-mountain-fragrance-advancement.json')
 assert report['version']=='A2.7.53'
 assert report['java_advancement']=='mountain_fragrance'
 assert report['trigger']=='empty-hand harvest of fruiting Pepper Leaves'
 assert report['xp_reward']==25
 assert report['once_per_player'] is True
 assert report['announce_to_chat'] is True
 assert report['shared_advancement_adapter'] is True
 assert report['new_poll_loop'] is False and report['new_world_event_listener'] is False
 assert report['native_java_advancement_tree'] is False and report['native_java_toast'] is False
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
  'version':'A2.7.53',
  'mountain_fragrance_advancement':True,
  'xp_reward':25,
  'once_per_player':True,
  'chat_announcement':True,
  'shared_advancement_adapter':True,
  'new_event_listener':False,
  'native_java_advancement_ui':False,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2753-dash-verification.json' if a.compiled else 'a2753-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
