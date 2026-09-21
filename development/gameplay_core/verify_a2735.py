from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
CORE='a2735_typed_oil_pot_block_core.js';RUNTIME='a2735_typed_oil_pot_block_runtime.js'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json');assert bm['header']['version']==[2,7,35] and rm['header']['version']==[2,7,35]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.35 Typed Cookery Oil Pot Block BP'
 for name in (CORE,RUNTIME):assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8');assert "import './a2735_typed_oil_pot_block_runtime.js';" in main_text
 runtime=(BP/'scripts'/RUNTIME).read_text(encoding='utf-8')
 for token in ('readCookeryOilPotForPlacement','blocksNativeCookeryInteraction','world.beforeEvents.playerBreakBlock','world.beforeEvents.explosion','e.setImpactedBlocks(keep)','buildCookeryOilPot(type,count)','planPlacedTypedOilAddition'):
  assert token in runtime,token
 assert "new ItemStack('kaleidoscope_grilling:" not in runtime
 subprocess.run(['node',str(DEV/'test_a2735_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 report=load(P/'reports/a2735-typed-oil-pot-block.json');assert report['version']=='A2.7.35';assert report['after']['new_grilling_oil_pot_block'] is False
 assert report['after']['placement_type_bridge'] is True and report['after']['explosion_preserves_type'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 result={'version':'A2.7.35','typed_oil_pot_block_bridge':True,'uses_cookery_host_block':True,'placement_type_bridge':True,'typed_capacity':64,'player_break_preserves_type':True,'explosion_preserves_type':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2735-dash-verification.json' if a.compiled else 'a2735-structure-verification.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
