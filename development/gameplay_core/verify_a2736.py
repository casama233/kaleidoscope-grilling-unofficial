from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
CORE='a2736_typed_oil_pot_block_core.js';RUNTIME='a2736_typed_oil_pot_block_runtime.js'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,36] and rm['header']['version']==[2,7,36]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.36 Typed Cookery Oil Pot Block BP'
 for name in (CORE,RUNTIME):assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2736_typed_oil_pot_block_runtime.js';" in main_text
 assert "from './a2735_player_io.js';" in main_text

 runtime=(BP/'scripts'/RUNTIME).read_text(encoding='utf-8')
 for token in (
  "from './a2734_cookery_oil_pot_adapter.js';",
  "from './a2735_player_io.js';",
  'readCookeryOilPotForPlacement','blocksNativeCookeryInteraction',
  'world.beforeEvents.playerBreakBlock.subscribe','world.beforeEvents.explosion.subscribe',
  'e.setImpactedBlocks(keep)','buildCookeryOilPot(type,count)','planPlacedTypedOilAddition'
 ):
  assert token in runtime,token
 assert 'EquipmentSlot' not in runtime and 'GameMode' not in runtime
 for fn in ('playerInventory','getMainHand','getOffHand','findHand','setHand','creative'):
  assert not re.search(rf'\bfunction\s+{fn}\s*\(',runtime),fn
 assert "new ItemStack('kaleidoscope_grilling:" not in runtime

 subprocess.run(['node',str(DEV/'test_a2736_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2736-typed-oil-pot-block.json')
 assert report['version']=='A2.7.36'
 assert report['reuse']['a2734_oil_adapter'] is True and report['reuse']['a2735_shared_player_io'] is True
 assert report['reuse']['new_grilling_oil_pot_block'] is False
 assert report['after']['placement_type_bridge'] is True
 assert report['after']['typed_capacity_clamped_to_64'] is True
 assert report['after']['host_duplicate_drop_avoided'] is True
 assert report['after']['player_break_preserves_type'] is True and report['after']['explosion_preserves_type'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Preserve the A2.7.35 dedupe rather than reintroducing local player IO.
 io=BP/'scripts/a2735_player_io.js';assert io.is_file()
 for name in ('main.js','a25_plate_recipe_runtime.js','a26_oil_machine_runtime.js','a2722_cold_houttuynia_runtime.js','a23_oil_world.js'):
  text=(BP/'scripts'/name).read_text(encoding='utf-8');assert "from './a2735_player_io.js';" in text,name

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

 result={'version':'A2.7.36','typed_oil_pot_block_bridge':True,'uses_cookery_host_block':True,'reuses_a2735_player_io':True,'typed_capacity':64,'bucket_points':8,'player_break_preserves_type':True,'explosion_preserves_type':True,'host_duplicate_drop_avoided':True,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2736-dash-verification.json' if a.compiled else 'a2736-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
