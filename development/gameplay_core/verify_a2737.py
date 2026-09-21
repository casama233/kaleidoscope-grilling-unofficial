from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
CORE='a2737_offhand_oil_fill_core.js';RUNTIME='a2737_offhand_oil_fill_runtime.js'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,37] and rm['header']['version']==[2,7,37]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.37 Offhand Oil Pot Fill BP'
 for name in (CORE,RUNTIME):assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2736_typed_oil_pot_block_runtime.js';" in main_text
 assert "import './a2737_offhand_oil_fill_runtime.js';" in main_text

 runtime=(BP/'scripts'/RUNTIME).read_text(encoding='utf-8')
 for token in (
  "import {OIL_TYPES} from './a23_oil_world.js';",
  "from './a2734_cookery_oil_pot_adapter.js';",
  "from './a2735_player_io.js';",
  'world.beforeEvents.itemUse.subscribe',
  'planCookeryTypedOilAddition',
  'planOffhandOilFill',
  'ev.cancel=true',
  "new ItemStack('minecraft:bucket',1)",
  'setOffHand(player,plan.next)',
  'post'
 ):
  if token=='post':continue
  assert token in runtime,token

 for forbidden in (
  'kaleidoscope_grilling:canola_oil_bucket',
  'kaleidoscope_grilling:secret_chili_oil_bucket',
  'kaleidoscope_grilling:premium_chili_oil_bucket',
  'kc_oil_count',
  'kaleidoscope_grilling:oil_type',
 ):
  assert forbidden not in runtime,forbidden

 assert 'EquipmentSlot' not in runtime and 'GameMode' not in runtime
 for fn in ('playerInventory','getMainHand','getOffHand','setMainHand','setOffHand','creative'):
  assert not re.search(rf'\bfunction\s+{fn}\s*\(',runtime),fn

 subprocess.run(['node',str(DEV/'test_a2737_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2737-offhand-oil-fill.json')
 assert report['version']=='A2.7.37'
 assert report['java_1_1_1']['main_hand_only'] is True
 assert report['java_1_1_1']['bucket_points']==8
 assert report['reuse']['new_bucket_registry'] is False
 assert report['reuse']['direct_host_dynamic_property_access'] is False
 assert report['after']['post_commit_verification_and_rollback'] is True
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

 result={'version':'A2.7.37','offhand_oil_pot_item_fill':True,'reuses_oil_registry':True,'reuses_a2734_adapter':True,'reuses_a2735_player_io':True,'bucket_points':8,'typed_capacity':64,'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a2737-dash-verification.json' if a.compiled else 'a2737-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
