from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess,re

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

MIGRATED=(
 'main.js',
 'a25_plate_recipe_runtime.js',
 'a26_oil_machine_runtime.js',
 'a2722_cold_houttuynia_runtime.js',
 'a23_oil_world.js',
)
LOCAL_BASIC_NAMES=(
 'mainContainer','playerContainer','inventory','heldMain','main','heldOff','off',
 'setMain','setOff','heldByHand','held','handFor','findHand','setHand','creative'
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,35] and rm['header']['version']==[2,7,35]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.35 Shared Player IO BP'

 io=BP/'scripts/a2735_player_io.js'
 assert io.read_bytes()==(DEV/'a2735_player_io.js').read_bytes()
 io_text=io.read_text(encoding='utf-8')
 for token in (
  'export function playerInventory',
  'export function getMainHand',
  'export function setMainHand',
  'export function getOffHand',
  'export function setOffHand',
  'export function getHand',
  'export function setHand',
  'export function findHand',
  'export function findHandEntry',
  'export function isCreative',
 ):
  assert token in io_text,token

 for name in MIGRATED:
  text=(BP/'scripts'/name).read_text(encoding='utf-8')
  assert "from './a2735_player_io.js';" in text,name
  first=text.splitlines()[0]
  assert 'EquipmentSlot' not in first,(name,first)
  assert 'GameMode' not in first,(name,first)
  for fn in LOCAL_BASIC_NAMES:
   assert not re.search(rf'\bfunction\s+{re.escape(fn)}\s*\(',text),(name,fn)

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert 'playerInventory as mainContainer' in main_text
 assert 'findHandEntry as handFor' in main_text
 assert 'isCreative as creative' in main_text

 plate=(BP/'scripts/a25_plate_recipe_runtime.js').read_text(encoding='utf-8')
 assert 'playerInventory as mainContainer' in plate
 assert 'getMainHand as heldMain' in plate and 'getOffHand as heldOff' in plate

 oil_machine=(BP/'scripts/a26_oil_machine_runtime.js').read_text(encoding='utf-8')
 assert 'findHand as handFor' in oil_machine and 'getHand as held' in oil_machine
 assert 'isCreative as creative' in oil_machine

 cold=(BP/'scripts/a2722_cold_houttuynia_runtime.js').read_text(encoding='utf-8')
 assert 'playerInventory as inventory' in cold
 assert 'setMainHand as setMain' in cold and 'setOffHand as setOff' in cold

 oil_world=(BP/'scripts/a23_oil_world.js').read_text(encoding='utf-8')
 assert 'findHand,setHand,isCreative as creative' in oil_world
 assert "from './a2734_cookery_oil_pot_adapter.js';" in oil_world

 # Intentionally specialized consumers retain writable EquipmentSlot access.
 beef=(BP/'scripts/a279_beef_board_runtime.js').read_text(encoding='utf-8')
 crop=(BP/'scripts/a2731_farmland_crop_host_runtime.js').read_text(encoding='utf-8')
 assert 'EquipmentSlot.Mainhand' in beef and 'getEquipmentSlot' in beef
 assert 'EquipmentSlot.Mainhand' in crop and 'EquipmentSlot.Offhand' in crop and 'getEquipmentSlot' in crop

 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2735_player_io.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2735-player-io.json')
 assert report['version']=='A2.7.35'
 assert len(report['migrated_consumers'])==5
 assert report['before']['duplicated_player_io_helper_sets']==5
 assert report['after']['shared_player_io_modules']==1
 assert report['after']['migrated_consumer_local_basic_hand_io_helpers']==0
 assert 'a279_beef_board_runtime.js' in report['intentionally_not_migrated']
 assert 'a2731_farmland_crop_host_runtime.js' in report['intentionally_not_migrated']
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Preserve A2.7.34 and recent visual/runtime architecture.
 assert "from './a2734_cookery_oil_pot_adapter.js';" in main_text
 assert "import './a2732_standalone_food_effect_runtime.js';" in main_text
 hand=load(RP/'attachables/special_seasoning.attachable.json')['minecraft:attachable']['description']
 assert hand['geometry']=={'default':'geometry.kg_a2733.seasoning_bottle_hand'}

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
  'version':'A2.7.35',
  'shared_player_io':True,
  'migrated_consumers':5,
  'local_basic_hand_io_helpers_after':0,
  'specialized_slot_consumers_retained':2,
  'a2734_oil_contract_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2735-dash-verification.json' if a.compiled else 'a2735-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
