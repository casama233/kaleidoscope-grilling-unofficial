from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
SCRIPTS=('a2756_advancement_event_core.js','a2756_advancement_event_runtime.js')
IDS=('looking_the_part','gleaming_with_oil','three_flavors_base','world_in_a_bottle','eat_it_hot','neat_and_orderly')

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,56] and rm['header']['version']==[2,7,56]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.56 Event Advancement Parity BP'
 for name in SCRIPTS:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 core=(BP/'scripts/a2756_advancement_event_core.js').read_text(encoding='utf-8')
 runtime=(BP/'scripts/a2756_advancement_event_runtime.js').read_text(encoding='utf-8')
 shared=(BP/'scripts/a2753_advancement_runtime.js').read_text(encoding='utf-8')
 assert "from './a2753_advancement_core.js'" in core
 assert "from './a2753_advancement_runtime.js'" in runtime
 assert 'awardOneShotAdvancement' in runtime
 for forbidden in ('getDynamicProperty','setDynamicProperty','addExperience','world.sendMessage','system.runInterval','subscribe('):
  assert forbidden not in runtime,forbidden
 for token in ('claimed(player,key)','markClaimed(player,key)','player.addExperience','world.sendMessage'):
  assert token in shared,token

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("from './a2756_advancement_event_runtime.js'")==1
 for token in ('awardLookingThePart(player,outcome);','awardSeasoningMilestones(player,top.ingredients);','awardEatItHot(player,id,meta.hot);'):
  assert main_text.count(token)==1,token
 assert main_text.count('awardGleamingWithOil(player);')==2

 rack=(BP/'scripts/a2746_advanced_rack_runtime.js').read_text(encoding='utf-8')
 assert rack.count("import {awardNeatAndOrderly} from './a2756_advancement_event_runtime.js';")==1
 assert rack.count('awardNeatAndOrderly(player);')==1
 assert 'world.beforeEvents.playerInteractWithBlock.subscribe' in rack
 assert rack.count('.subscribe(')==3  # existing interact, break, explosion only

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for id in IDS:
   for suffix in ('title','description'):
    key=f'advancement.kaleidoscope_grilling.{id}.{suffix}'
    assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2756_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2756-event-advancement-parity.json')
 assert report['version']=='A2.7.56'
 assert report['event_advancements']==list(IDS)
 assert report['reuse']['one_shot_adapter']=='a2753_advancement_runtime.js'
 assert report['reuse']['new_listener_count']==0
 assert report['reuse']['new_interval_count']==0
 assert report['reuse']['duplicate_progression_store'] is False
 assert report['fortress_wart_replacement']['implemented'] is False
 assert report['fortress_wart_replacement']['platform_blocked_without_intrusive_scan'] is True
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
  'version':'A2.7.56','event_advancement_parity':True,'advancement_count':6,
  'shared_a2753_adapter':True,'new_listener_count':0,'new_interval_count':0,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2756-dash-verification.json' if a.compiled else 'a2756-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
