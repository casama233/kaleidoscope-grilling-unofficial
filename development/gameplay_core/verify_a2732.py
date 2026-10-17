from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)

 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,32] and rm['header']['version']==[2,7,32]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.32 Standalone Food Effects BP'

 core=BP/'scripts/a2732_standalone_food_effect_core.js'
 runtime=BP/'scripts/a2732_standalone_food_effect_runtime.js'
 assert core.read_bytes()==(DEV/'a2732_standalone_food_effect_core.js').read_bytes()
 assert runtime.read_bytes()==(DEV/'a2732_standalone_food_effect_runtime.js').read_bytes()

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a2732_standalone_food_effect_runtime.js';" in main
 assert "import './a2720_roasted_sweet_potato_runtime.js';" not in main
 assert "import './a2722_cold_houttuynia_runtime.js';" in main
 assert 'COOKED_EFFECTS' in main and 'applyFixedEffect' in main

 cold=(BP/'scripts/a2722_cold_houttuynia_runtime.js').read_text(encoding='utf-8')
 assert 'itemCompleteUse.subscribe' not in cold
 assert "addEffect('fire_resistance'" not in cold
 assert 'FIRE_RESISTANCE_TICKS' not in cold
 assert 'tryCraftColdHouttuynia' in cold
 assert 'playerInteractWithBlock.subscribe' in cold

 rt=runtime.read_text(encoding='utf-8')
 assert rt.count('itemCompleteUse.subscribe')==1
 assert 'applyStandaloneFoodEffects' in rt
 assert 'applyPersistent' in rt and 'applyNative' in rt

 table=core.read_text(encoding='utf-8')
 for token in (
  "itemId:ROASTED_ID",
  "effect:WARMTH_EFFECT",
  "ticks:WARMTH_TICKS",
  "itemId:COLD_ID",
  "effect:'fire_resistance'",
  "ticks:FIRE_RESISTANCE_TICKS",
 ):
  assert token in table,token

 # Historical modules remain available for the old slice verifiers, but current main no longer executes roasted's listener.
 assert (BP/'scripts/a2720_roasted_sweet_potato_runtime.js').is_file()

 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2732_core.mjs')],check=True)
 subprocess.run(['node','--experimental-vm-modules',str(ROOT/'development/gameplay_core/test_a2732_runtime.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2720_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a2722_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2732-standalone-food-effects.json')
 assert report['version']=='A2.7.32'
 assert report['existing_main_skewer_effect_registry_preserved'] is True
 assert report['before']['standalone_item_complete_use_subscribers']==2
 assert report['after']['standalone_item_complete_use_subscribers']==1
 assert report['after']['registry_rows']==2
 assert report['cold_houttuynia_crafting_runtime_retained'] is True
 assert report['future_ready_for_multi_effect_foods'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # Prior architecture fixes remain active.
 assert "import './a2727_cookery_host_recipes_runtime.js';" in main
 assert "from './a2730_cookery_oil_pot_adapter.js';" in main
 assert "import './a2731_farmland_crop_host_runtime.js';" in main
 tw=(RP/'texts/zh_TW.lang').read_text(encoding='utf-8-sig')
 assert '森羅物語：煙火' in tw and '烤饅頭片串' in tw

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
  'version':'A2.7.32',
  'standalone_food_effect_registry':True,
  'registry_rows':2,
  'active_standalone_effect_runtime_modules':1,
  'active_standalone_item_complete_use_subscribers':1,
  'cold_houttuynia_crafting_preserved':True,
  'main_skewer_effect_registry_preserved':True,
  'a2731_crop_host_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2732-dash-verification.json' if a.compiled else 'a2732-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':
 main()
