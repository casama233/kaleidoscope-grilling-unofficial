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
 assert bm['header']['version']==[2,7,7] and rm['header']['version']==[2,7,7]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.7 Transaction Rollback BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.7 Transaction Rollback RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 helper=(BP/'scripts/a277_grill_transaction_core.js').read_text(encoding='utf-8')
 for token in ('commitTwoParty','rollbackSecondary','rollbackPrimary','chooseExtractDelivery','breakEscrowDropCount'):assert token in helper,token

 runtime=(BP/'scripts/main.js').read_text(encoding='utf-8')
 required=(
  "import {commitTwoParty,chooseExtractDelivery} from './a277_grill_transaction_core.js';",
  'function planDamagedHand(player,hand,amount=1)',
  'function commitGrillAndHand(block,beforeState,nextState,player,hand,beforeStack,nextStack,mutateHand=true)',
  'function firstEmptyPlayerSlot(player)',
  'function deliverExtractOutput(player,stack)',
  "const state=readState(block);if(!canExtract(state))return 0;const c=inv(block);if(!c)return 0;let count=0,aborted=false;",
  "try{c.setItem(i,undefined)}catch{aborted=true;break}",
  "catch{try{c.setItem(i,raw)}catch{};message(player,'§c取串失敗，原串已嘗試回滾');aborted=true;break}",
  'if(!aborted&&occupied(block)===0)resetBlock(block,state.lit)',
  'function removeEscrow(entities){for(const e of entities)try{e?.remove()}catch{}}',
  'function restoreBrokenGrill(dim,loc,permutation,state,raws)',
  'for(let i=0;i<drops.length;i++)escrow.push(dim.spawnItem',
  "clearContainer(block);clearState(block);removeGrillLegs(block);block.setType('minecraft:air')",
  'removeEscrow(escrow);restoreBrokenGrill',
  'function planCookeryOil(player,hand,needed)',
  'function planSeasoningBottle(player,hand,needed)',
  'const tool=planDamagedHand(player,hand,1),nextState=light(state,true)',
  'commitGrillAndHand(block,state,nextState,player,hand,tool.before,tool.next,tool.mutate)',
  'const oil=planCookeryOil(player,hand,n)',
  'commitGrillAndHand(block,state,result.state,player,hand,oil.before,oil.next,oil.mutate)',
  'const bottle=planSeasoningBottle(player,hand,n)',
  'commitGrillAndHand(block,state,result.state,player,hand,bottle.before,bottle.next,bottle.mutate)'
 )
 for token in required:assert token in runtime,token
 for forbidden in ('function consumeCookeryOil(player,hand,needed)','function consumeSeasoningBottle(player,hand,needed)','function damageHandTool(player,hand,amount=1)'):
  assert forbidden not in runtime,forbidden

 # Ordering checks: source slot is cleared before delivery; break drops are escrowed before destructive commit.
 extract_start=runtime.index('function extract(block,player,all=false)')
 extract_end=runtime.index('function removeEscrow',extract_start)
 extract_src=runtime[extract_start:extract_end]
 assert extract_src.index('c.setItem(i,undefined)')<extract_src.index('deliverExtractOutput(player,output)')
 break_start=runtime.index('function customBreak(block,player)')
 break_end=runtime.index('function cookeryOilType',break_start)
 break_src=runtime[break_start:break_end]
 assert break_src.index('dim.spawnItem')<break_src.index('clearContainer(block)')
 assert break_src.index('clearContainer(block)')<break_src.index("block.setType('minecraft:air')")

 # Prior stabilization stays intact.
 a276=load(P/'reports/a276-grill-intent-hand.json')
 assert a276['fixes']['deferred_toctou']['status']=='fixed'
 a275=load(P/'reports/a275-grill-input-hardening.json')
 assert a275['fixes']['held_block_interaction_repeat']['status']=='fixed'
 a274=load(P/'reports/a274-java-gui-icons.json')
 assert a274['exact_static_java_icons']==39 and len(a274['items'])==41
 assert (BP/'blocks/grill_legs.json').is_file()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a277_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a276_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a275_core.mjs')],check=True)
 for test in ('test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a271_core.mjs','test_a272_core.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/test)],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a277-grill-transaction-rollback.json')
 assert report['version']=='A2.7.7'
 assert report['fixes']['state_resource_commits']['status']=='fixed'
 assert report['fixes']['extract']['status']=='fixed'
 assert report['fixes']['break']['status']=='fixed'
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
  'version':'A2.7.7',
  'state_resource_rollback':True,
  'extract_source_first_delivery':True,
  'extract_delivery_rollback':True,
  'break_drop_escrow':True,
  'break_snapshot_restore':True,
  'entity_remove_cleanup':True,
  'a276_intent_hand_preserved':True,
  'a275_input_hardening_preserved':True,
  'a274_java_icons_preserved':True,
  'a273_grill_helper_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a277-dash-verification.json' if a.compiled else 'a277-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
