from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,32]

OLD_ROASTED_IMPORT="import './a2720_roasted_sweet_potato_runtime.js';"
NEW_EFFECT_IMPORT="import './a2732_standalone_food_effect_runtime.js';"

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'A2.7.32 patch anchor drift ({label}): {s.count(old)}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.32 Standalone Food Effects BP'),
  (rm,'Kaleidoscope Grilling A2.7.32 Standalone Food Effects RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.32 Standalone Food Effects'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_32_Standalone_Food_Effects'
 write(P/'config.json',cfg)

def patch_effect_host():
 shutil.copy2(DEV/'a2732_standalone_food_effect_core.js',BP/'scripts/a2732_standalone_food_effect_core.js')
 shutil.copy2(DEV/'a2732_standalone_food_effect_runtime.js',BP/'scripts/a2732_standalone_food_effect_runtime.js')

 main_path=BP/'scripts/main.js'
 s=main_path.read_text(encoding='utf-8')
 s=replace_once(s,OLD_ROASTED_IMPORT,NEW_EFFECT_IMPORT,'main standalone effect import')
 if s.count("import './a2722_cold_houttuynia_runtime.js';")!=1:
  raise RuntimeError('A2.7.32 cold crafting runtime import drift')
 main_path.write_text(s,encoding='utf-8')

 cold_path=BP/'scripts/a2722_cold_houttuynia_runtime.js'
 c=cold_path.read_text(encoding='utf-8')
 c=replace_once(
  c,
  " COLD_ID,HOUTTUYNIA_ID,CRAFTING_TABLE_ID,REQUIRED_OIL_TYPE,FIRE_RESISTANCE_TICKS,\n",
  " COLD_ID,HOUTTUYNIA_ID,CRAFTING_TABLE_ID,REQUIRED_OIL_TYPE,\n",
  'cold unused effect constant'
 )
 effect_block="""world.afterEvents.itemCompleteUse.subscribe(ev=>{
 if(ev.itemStack?.typeId!==COLD_ID)return;
 try{ev.source.addEffect('fire_resistance',FIRE_RESISTANCE_TICKS,{showParticles:true})}catch{}
});
"""
 c=replace_once(c,effect_block,'','cold per-food itemCompleteUse listener')
 cold_path.write_text(c,encoding='utf-8')

def report():
 write(P/'reports/a2732-standalone-food-effects.json',{
  'version':'A2.7.32',
  'scope':'consolidate standalone non-skewer food completion effects into one registry/handler',
  'existing_main_skewer_effect_registry_preserved':True,
  'standalone_foods':[
   {
    'item':'kaleidoscope_grilling:roasted_sweet_potato',
    'effect':'persistent warmth',
    'ticks':600,
    'stacking':'max(current_until, now+600)'
   },
   {
    'item':'kaleidoscope_grilling:cold_houttuynia',
    'effect':'minecraft fire_resistance',
    'ticks':1200
   }
  ],
  'before':{
   'standalone_food_effect_runtime_modules':2,
   'standalone_item_complete_use_subscribers':2
  },
  'after':{
   'standalone_food_effect_runtime_modules':1,
   'standalone_item_complete_use_subscribers':1,
   'registry_rows':2
  },
  'cold_houttuynia_crafting_runtime_retained':True,
  'old_roasted_runtime_retained_for_historical_slice_rebuilds':True,
  'old_cold_source_retained_in_development_history':True,
  'future_ready_for_multi_effect_foods':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,31]:
  raise RuntimeError('A2.7.32 must augment verified A2.7.31')
 patch_versions();patch_effect_host();report()
 print('A2.7.32 standalone food effect registry refactor complete')

if __name__=='__main__':
 main()
