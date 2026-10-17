from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,34]

OLD_ADAPTER="./a2730_cookery_oil_pot_adapter.js"
NEW_ADAPTER="./a2734_cookery_oil_pot_adapter.js"

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'A2.7.34 patch anchor drift ({label}): {s.count(old)}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.34 Cookery Oil Contract Fix BP'),
  (rm,'Kaleidoscope Grilling A2.7.34 Cookery Oil Contract Fix RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.34 Cookery Oil Contract Fix'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_34_Cookery_Oil_Contract_Fix'
 write(P/'config.json',cfg)

def patch_adapter():
 shutil.copy2(DEV/'a2734_cookery_oil_pot_core.js',BP/'scripts/a2734_cookery_oil_pot_core.js')
 shutil.copy2(DEV/'a2734_cookery_oil_pot_adapter.js',BP/'scripts/a2734_cookery_oil_pot_adapter.js')

 for name in ('main.js','a26_oil_machine_runtime.js','a2722_cold_houttuynia_runtime.js'):
  path=BP/'scripts'/name;s=path.read_text(encoding='utf-8')
  if s.count(OLD_ADAPTER)!=1:raise RuntimeError(f'A2.7.34 expected one A2.7.30 adapter import in {name}')
  path.write_text(s.replace(OLD_ADAPTER,NEW_ADAPTER,1),encoding='utf-8')

def patch_oil_world():
 path=BP/'scripts/a23_oil_world.js';s=path.read_text(encoding='utf-8')
 s=replace_once(
  s,
  "import {FLUID_CAPACITY,OIL_BUCKET_POINTS} from './a24_skewering_core.js';",
  "import {OIL_BUCKET_POINTS} from './a24_skewering_core.js';\nimport {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryTypedOilAddition} from './a2734_cookery_oil_pot_adapter.js';",
  'oil-world imports'
 )
 s=replace_once(
  s,
  "const COOKERY_EMPTY='kaleidoscope_cookery:oil_pot',COOKERY_FILLED='kaleidoscope_cookery:oil_pot_filled';\n",
  '',
  'oil-world duplicated Cookery IDs'
 )
 start=s.index('function cookeryType(stack)')
 end=s.index('function takeSource(',start)
 s=s[:start]+s[end:]
 old="""function takeSource(player,block,type,hand,toCookery=false){
 if(level(block)!==0)return false;
 const held=hand==='off'?off(player):main(player);
 let nextPot;
 if(toCookery){
  const currentType=held?.typeId===COOKERY_FILLED?cookeryType(held):'',current=held?.typeId===COOKERY_FILLED?cookeryCount(held):0;
  if((currentType&&currentType!==type)||current+OIL_BUCKET_POINTS>FLUID_CAPACITY)return false;
  nextPot=new ItemStack(COOKERY_FILLED,1);
  try{
   const next=current+OIL_BUCKET_POINTS;
   nextPot.setLore(['§7Oil: '+next+'/'+FLUID_CAPACITY]);
   nextPot.setDynamicProperty('kc_oil_count',next);
   nextPot.setDynamicProperty('kaleidoscope_grilling:oil_type',type);
  }catch{}
 }
 const rows=readReg(),k=posKey(block.dimension.id,block.x,block.y,block.z),row=rows.find(r=>r.k===k);
 try{block.setType('minecraft:air')}catch{return false}
 if(row){clearCells(row,rows);saveReg(rows.filter(r=>r!==row))}
 if(toCookery)setHand(player,hand,nextPot);else setHand(player,hand,new ItemStack(OIL_TYPES[type].bucket,1));
 return true;
}
"""
 new="""function takeSource(player,block,type,hand,toCookery=false){
 if(level(block)!==0)return false;
 const held=hand==='off'?off(player):main(player);
 let nextPot;
 if(toCookery){
  const plan=planCookeryTypedOilAddition(held,type,OIL_BUCKET_POINTS);
  if(!plan.ok)return false;
  nextPot=plan.next;
 }
 const rows=readReg(),k=posKey(block.dimension.id,block.x,block.y,block.z),row=rows.find(r=>r.k===k);
 try{block.setType('minecraft:air')}catch{return false}
 if(row){clearCells(row,rows);saveReg(rows.filter(r=>r!==row))}
 if(toCookery)setHand(player,hand,nextPot);else setHand(player,hand,new ItemStack(OIL_TYPES[type].bucket,1));
 return true;
}
"""
 s=replace_once(s,old,new,'oil-world source-to-pot contract')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2734-oil-contract-fix.json',{
  'version':'A2.7.34',
  'scope':'correct Cookery oil-pot read modes and route the missed world-oil consumer through one adapter',
  'audit_finding':{
   'a2730_claimed_active_consumers':3,
   'actual_active_consumers_before_a2734':4,
   'missed_consumer':'a23_oil_world.js',
   'a2730_conflated_normal_item_read_with_legacy_placement_fallback':True
  },
  'cookery_bedrock_1_0_6':{
   'normal_item_read_missing_count':0,
   'legacy_filled_item_placement_missing_count':256,
   'native_capacity':256,
   'host_count_key':'kc_oil_count'
  },
  'java_1_1_1':{
   'get_count_missing_component':0,
   'fat_capacity':256,
   'typed_fluid_capacity':64
  },
  'active_consumers_after':[
   'main.js grill brushing',
   'a26_oil_machine_runtime.js Big Vat filling',
   'a2722_cold_houttuynia_runtime.js premium chili consumption',
   'a23_oil_world.js source pickup into Cookery pot'
  ],
  'after':{
   'active_adapter':'a2734_cookery_oil_pot_adapter.js',
   'active_consumers':4,
   'consumer_direct_host_key_access':0,
   'consumer_direct_host_item_id_literals':0,
   'normal_missing_count_fallback':0,
   'legacy_placement_fallback_exposed_separately':True,
   'native_fat_retyping_blocked':True
  },
  'remaining_infrastructure_duplicates':[
   'player hand/inventory/creative helpers across active runtimes',
   'face/offset and coordinate-key helpers',
   'per-slice manifest/version/package CI boilerplate'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,33]:
  raise RuntimeError('A2.7.34 must augment verified A2.7.33')
 patch_versions();patch_adapter();patch_oil_world();report()
 print('A2.7.34 Cookery oil contract fix complete')

if __name__=='__main__':
 main()
