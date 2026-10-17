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
 assert bm['header']['version']==[2,7,6] and rm['header']['version']==[2,7,6]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.6 Grill Intent/Hand Parity BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.6 Grill Intent/Hand Parity RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 helper=(BP/'scripts/a276_grill_intent_core.js').read_text(encoding='utf-8')
 for token in ('chooseInteractionHand','makeIntent','intentMatches','currentOffSig','selectedSlot'):assert token in helper,token

 runtime=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  "import {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';",
  "function heldByHand(player,hand)",
  "function decrementHand(player,hand,count=1)",
  "function damageHandTool(player,hand,amount=1)",
  "function stackIntentSignature(stack)",
  "function captureGrillIntent(player,eventStack)",
  "function grillIntentStillCurrent(player,intent)",
  "function consumeCookeryOil(player,hand,needed)",
  "function consumeSeasoningBottle(player,hand,needed)",
  "function handleGrill(block,player,hand='main')",
  "damageHandTool(player,hand,1)",
  "consumeCookeryOil(player,hand,n)",
  "consumeSeasoningBottle(player,hand,n)",
  "decrementHand(player,hand)",
  "animation.kg_imm.player.brush.'+hand",
  "animation.kg_imm.player.season.'+hand",
  "animation.kg_imm.player.reach.'+hand",
  "intent=grillTarget?captureGrillIntent(p,e.itemStack):null",
  "if(!grillIntentStillCurrent(p,intent))",
  "handleGrill(block,p,intent.hand)",
  "c.setItem(slot,undefined);message(player,'§c手中物品已變更，插串已取消')"
 ):assert token in runtime,token
 assert 'function damageMainTool(' not in runtime
 assert 'consumeCookeryOil(player,n)' not in runtime
 assert 'consumeSeasoningBottle(player,n)' not in runtime

 # Previous stabilization must remain intact.
 a275=load(P/'reports/a275-grill-input-hardening.json')
 assert a275['fixes']['held_block_interaction_repeat']['status']=='fixed'
 a274=load(P/'reports/a274-java-gui-icons.json')
 assert a274['exact_static_java_icons']==39 and len(a274['items'])==41
 assert (BP/'blocks/grill_legs.json').is_file()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a276_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a275_core.mjs')],check=True)
 for test in ('test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a276-grill-intent-hand.json')
 assert report['version']=='A2.7.6'
 assert report['fixes']['deferred_toctou']['status']=='fixed'
 assert report['fixes']['interaction_hand']['status']=='ported_with_ambiguity_fallback'
 assert report['fixes']['hand_transactions']['status']=='fixed'
 assert report['fixes']['insert_rollback']['status']=='fixed'
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
  'version':'A2.7.6',
  'deferred_intent_snapshot':True,
  'main_offhand_grill_transactions':True,
  'stale_intent_aborts':True,
  'insert_rollback_on_decrement_failure':True,
  'identical_two_hand_ambiguity_fallback':'main',
  'a275_input_hardening_preserved':True,
  'a274_java_icons_preserved':True,
  'a273_grill_helper_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a276-dash-verification.json' if a.compiled else 'a276-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
