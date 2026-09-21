from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent
VERSION=[2,7,30]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'A2.7.30 patch anchor drift ({label}): {s.count(old)}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.30 Cookery Oil Pot Adapter BP'),
  (rm,'Kaleidoscope Grilling A2.7.30 Cookery Oil Pot Adapter RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.30 Cookery Oil Pot Adapter'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_30_Cookery_Oil_Pot_Adapter'
 write(P/'config.json',cfg)

def patch_main():
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2727_cookery_host_recipes_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport {COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryOilPotConsumption} from './a2730_cookery_oil_pot_adapter.js';",'main adapter import')
 old_const="const COOKERY_POT='kaleidoscope_cookery:oil_pot',COOKERY_FILLED='kaleidoscope_cookery:oil_pot_filled',COOKERY_OIL_KEY='kc_oil_count';\n"
 s=replace_once(s,old_const,'','main duplicated oil constants')
 start=s.index('function cookeryOilType(stack)')
 end=s.index('function planSeasoningBottle',start)
 replacement="""function heatForOil(type){return OIL_TYPES[type]?.heatTicks??OIL_TYPES.canola.heatTicks}
function planCookeryOil(player,hand,needed){
 const stack=heldByHand(player,hand),oil=planCookeryOilPotConsumption(stack,needed);
 if(!oil.ok)return oil;
 const heat=heatForOil(oil.type);
 if(creative(player))return {...oil,heat,remaining:oil.count,next:oil.before.clone(),mutate:false};
 return {...oil,heat,mutate:true};
}
"""
 s=s[:start]+replacement+s[end:]
 path.write_text(s,encoding='utf-8')

def patch_oil_machine():
 path=BP/'scripts/a26_oil_machine_runtime.js';s=path.read_text(encoding='utf-8')
 anchor="} from './a26_oil_machine_core.js';"
 s=replace_once(s,anchor,anchor+"\nimport {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,readCookeryOilPot,buildCookeryOilPot} from './a2730_cookery_oil_pot_adapter.js';",'a26 adapter import')
 s=replace_once(s,"const COOKERY_EMPTY='kaleidoscope_cookery:oil_pot';\nconst COOKERY_FILLED='kaleidoscope_cookery:oil_pot_filled';\n",'','a26 duplicated ids')
 start=s.index('function potType(stack)')
 end=s.index('function bucketType(id)',start)
 s=s[:start]+s[end:]
 s=replace_once(
  s,
  " const type=item.typeId===COOKERY_FILLED?potType(item):'',count=item.typeId===COOKERY_FILLED?potCount(item):0;\n",
  " const oil=readCookeryOilPot(item),type=item.typeId===COOKERY_FILLED?oil.type:'',count=item.typeId===COOKERY_FILLED?oil.count:0;\n",
  'a26 read oil pot'
 )
 s=replace_once(
  s,
  " const pot=filledPot(plan.type,plan.nextCount);if(pot)setHand(p,hand,pot);writeVat(block,next.state);return true;\n",
  " const pot=buildCookeryOilPot(plan.type,plan.nextCount,item);if(pot)setHand(p,hand,pot);writeVat(block,next.state);return true;\n",
  'a26 build oil pot'
 )
 path.write_text(s,encoding='utf-8')

def patch_cold_houttuynia():
 path=BP/'scripts/a2722_cold_houttuynia_runtime.js';s=path.read_text(encoding='utf-8')
 old="""import {
 COLD_ID,HOUTTUYNIA_ID,CRAFTING_TABLE_ID,COOKERY_EMPTY_ID,COOKERY_FILLED_ID,
 REQUIRED_OIL_TYPE,OIL_TYPE_KEY,OIL_COUNT_KEY,OIL_CAPACITY,FIRE_RESISTANCE_TICKS,
 planColdHouttuynia,nextOilPotId
} from './a2722_cold_houttuynia_core.js';
"""
 new="""import {
 COLD_ID,HOUTTUYNIA_ID,CRAFTING_TABLE_ID,REQUIRED_OIL_TYPE,FIRE_RESISTANCE_TICKS,
 planColdHouttuynia
} from './a2722_cold_houttuynia_core.js';
import {
 COOKERY_FILLED_ID,readCookeryOilPot,buildCookeryOilPot
} from './a2730_cookery_oil_pot_adapter.js';
"""
 s=replace_once(s,old,new,'cold imports')
 start=s.index('function oilType(stack)')
 end=s.index('function message(player,text)',start)
 s=s[:start]+s[end:]
 start=s.index('function nextOilStack(stack,count,type)')
 end=s.index('function failureText(reason)',start)
 s=s[:start]+s[end:]
 s=replace_once(
  s,
  " const m=main(player),o=off(player),type=oilType(o),count=oilCount(o);\n",
  " const m=main(player),o=off(player),oil=readCookeryOilPot(o),type=oil.type,count=oil.count;\n",
  'cold read oil pot'
 )
 s=replace_once(
  s,
  " const afterOff=nextOilStack(o,plan.nextOilCount,type);\n",
  " const afterOff=buildCookeryOilPot(type,plan.nextOilCount,o);if(!afterOff)return false;\n",
  'cold next oil pot'
 )
 path.write_text(s,encoding='utf-8')

def patch_adapter():
 shutil.copy2(DEV/'a2730_cookery_oil_pot_core.js',BP/'scripts/a2730_cookery_oil_pot_core.js')
 shutil.copy2(DEV/'a2730_cookery_oil_pot_adapter.js',BP/'scripts/a2730_cookery_oil_pot_adapter.js')

def report():
 write(P/'reports/a2730-oil-pot-adapter.json',{
  'version':'A2.7.30',
  'scope':'centralize Cookery oil-pot state access for all active Grilling consumers',
  'cookery_host':{
   'version':'1.0.6','curseforge_project_id':1673664,'file_id':8908596,
   'archive_sha256':'c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351',
   'empty_item':'kaleidoscope_cookery:oil_pot',
   'filled_item':'kaleidoscope_cookery:oil_pot_filled',
   'host_count_key':'kc_oil_count','native_fat_capacity':256
  },
  'grilling_extension':{
   'type_key':'kaleidoscope_grilling:oil_type','typed_capacity':64,
   'types':['canola','secret_chili','premium_chili']
  },
  'active_consumers':[
   'main.js grill brushing',
   'a26_oil_machine_runtime.js Big Vat filling',
   'a2722_cold_houttuynia_runtime.js premium chili consumption'
  ],
  'before':{'independent_oil_pot_readers':3,'independent_oil_pot_builders_or_consumers':3},
  'after':{'shared_adapter_modules':1,'consumer_direct_host_key_access':0,'consumer_direct_host_item_id_literals':0},
  'behavior':{
   'untyped_host_fat_capacity':256,'typed_grilling_oil_capacity':64,
   'missing_count_fallback_uses_capacity':True,'zero_remaining_returns_empty_host_pot':True,
   'existing_filled_stack_metadata_preserved_by_clone':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,29]:
  raise RuntimeError('A2.7.30 must augment verified A2.7.29')
 patch_versions();patch_adapter();patch_main();patch_oil_machine();patch_cold_houttuynia();report()
 print('A2.7.30 Cookery oil-pot adapter refactor complete')

if __name__=='__main__':main()
