from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
NEW=('a2760_advancement_inventory_core.js','a2760_advancement_inventory_runtime.js')
IDS=('human_fireworks','better_write_it_down','a_handful_of_canola','strength_makes_oil','sweet_potato','nether_taste')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json');assert bm['header']['version']==[2,7,60] and rm['header']['version']==[2,7,59]
 for n in NEW:assert (BP/'scripts'/n).read_bytes()==(DEV/n).read_bytes(),n
 rt=(BP/'scripts/a2760_advancement_inventory_runtime.js').read_text(encoding='utf-8')
 for t in ("RAW_TO_COOKED","playerInventory,getOffHand","awardOneShotAdvancement","Object.keys(RAW_TO_COOKED)","inventoryAdvancementIds"):assert t in rt,t
 for bad in ('system.runInterval(','subscribe(','setDynamicProperty','getDynamicProperty'):assert bad not in rt,bad
 maintext=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert maintext.count("import {awardInventoryAdvancements} from './a2760_advancement_inventory_runtime.js';")==1
 assert maintext.count('if(system.currentTick%20===0)awardInventoryAdvancements(p);')==1
 assert maintext.count('system.runInterval(')==1
 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  rows=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for id in IDS:
   for suffix in ('title','description'):
    key=f'advancement.kaleidoscope_grilling.{id}.{suffix}';assert sum(1 for x in rows if x.startswith(key+'='))==1,(lang,key)
 subprocess.run(['node',str(DEV/'test_a2760_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 r=load(P/'reports/a2760-inventory-advancement-parity.json');assert r['version']=='A2.7.60';assert r['cadence_ticks']==20;assert r['reuse']['new_interval_count']==0;assert r['reuse']['new_listener_count']==0;assert r['reuse']['raw_skewer_source']=='Object.keys(RAW_TO_COOKED)';assert r['minecraft_tested'] is False
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   m=load(source/'manifest.json');matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==m['header']['uuid']];assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 out=P/'reports'/('a2760-dash-verification.json' if a.compiled else 'a2760-structure-verification.json')
 out.write_text(json.dumps({'version':'A2.7.60','inventory_advancement_parity':True,'new_advancement_count':6,'looking_the_part_inventory_fallback':True,'new_interval_count':0,'new_listener_count':0,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False},indent=2)+'\n',encoding='utf-8');print(out.read_text())
if __name__=='__main__':main()
