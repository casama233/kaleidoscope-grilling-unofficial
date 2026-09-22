from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2758_advancement_challenge_core.js','a2758_advancement_challenge_runtime.js')
IDS=('mental_preparation_failed','metallic_taste','taste_of_dragon','metal_tolerance_failed','strongest_shield','strongest_spear','wedding_candy')

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,58] and rm['header']['version']==[2,7,58]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.58 Challenge Advancement Parity BP'

 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 assert (BP/'scripts/a2753_advancement_runtime.js').read_bytes()==(DEV/'a2758_refactored_a2753_advancement_runtime.js').read_bytes()
 assert (BP/'scripts/a2747_wedding_candy_runtime.js').read_bytes()==(DEV/'a2758_refactored_a2747_wedding_candy_runtime.js').read_bytes()

 shared=(BP/'scripts/a2753_advancement_runtime.js').read_text(encoding='utf-8')
 assert "from './a2758_advancement_challenge_core.js'" in shared
 assert 'advancementFrameTranslationKeys(spec.frame)' in shared
 assert "message.kaleidoscope_grilling.advancement.goal_announce" not in shared

 runtime=(BP/'scripts/a2758_advancement_challenge_runtime.js').read_text(encoding='utf-8')
 assert "from './a2753_advancement_runtime.js'" in runtime
 assert 'awardOneShotAdvancement' in runtime
 for forbidden in ('subscribe(','runInterval(','getDynamicProperty','setDynamicProperty','addExperience','world.sendMessage'):
  assert forbidden not in runtime,forbidden

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main.count("from './a2758_advancement_challenge_runtime.js'")==1
 assert main.count('awardMentalPreparationFailed(player,id);')==1
 assert main.count('awardSeasoningFinishedChallenges(player,list);')==1
 assert main.count('awardMetalToleranceFailed(player,c.totem,true);')==1
 assert main.count("const outcome=ordinaryChallengeOutcome(challenged,Math.random());")==1
 assert main.count("awardOrdinaryChallenge(player,outcome);")==2
 ordinary=main.split('function applyOrdinary(player){',1)[1].split('function afterCommitted',1)[0]
 assert ordinary.count('Math.random()')==1
 assert "challenged&&Math.random()<.5" not in ordinary

 wedding=(BP/'scripts/a2747_wedding_candy_runtime.js').read_text(encoding='utf-8')
 assert "import {awardWeddingCandy} from './a2758_advancement_challenge_runtime.js';" in wedding
 assert wedding.count('awardWeddingCandy(player);')==1
 assert 'rewardExperience' not in wedding
 assert 'addExperience' not in wedding
 assert "runCommand('xp " not in wedding
 assert wedding.count('system.runInterval(')==1

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for id in IDS:
   for suffix in ('title','description'):
    key=f'advancement.kaleidoscope_grilling.{id}.{suffix}'
    assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)
  for key in (
   'message.kaleidoscope_grilling.advancement.task_announce',
   'message.kaleidoscope_grilling.advancement.task_self',
   'message.kaleidoscope_grilling.advancement.challenge_announce',
   'message.kaleidoscope_grilling.advancement.challenge_self',
  ):
   assert sum(1 for row in rows if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2758_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2758-challenge-advancement-parity.json')
 assert report['version']=='A2.7.58'
 assert report['challenge_advancements']==list(IDS)
 assert report['reuse']['frame_aware_shared_adapter'] is True
 assert report['reuse']['new_listener_count']==0
 assert report['reuse']['new_interval_count']==0
 assert report['reuse']['duplicate_progression_store'] is False
 assert report['reuse']['existing_wedding_interval_reused'] is True
 assert report['wedding_candy']['direct_daily_xp_removed'] is True
 assert report['wedding_candy']['one_shot_advancement_xp']==50
 assert report['ordinary_skewer']['single_rng_result_shared_with_advancement'] is True
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
  'version':'A2.7.58','challenge_advancement_parity':True,'advancement_count':7,
  'shared_a2753_adapter':True,'frame_aware_messages':True,
  'new_listener_count':0,'new_interval_count':0,'wedding_daily_xp_bug_fixed':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2758-dash-verification.json' if a.compiled else 'a2758-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
