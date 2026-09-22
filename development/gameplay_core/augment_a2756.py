from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,56]
SCRIPTS=('a2756_advancement_event_core.js','a2756_advancement_event_runtime.js')
LANG={
 'en_US.lang':[
  'advancement.kaleidoscope_grilling.looking_the_part.title=Looking the Part',
  'advancement.kaleidoscope_grilling.looking_the_part.description=Finish assembling your first skewer.',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.title=Gleaming with Oil',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.description=Brush oil onto skewers for the first time.',
  'advancement.kaleidoscope_grilling.three_flavors_base.title=Three Flavors Base',
  'advancement.kaleidoscope_grilling.three_flavors_base.description=Place all three required seasonings into a bottle.',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.title=World in a Bottle',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.description=Fill a seasoning bottle with eight ingredients.',
  'advancement.kaleidoscope_grilling.eat_it_hot.title=Eat It Hot!',
  'advancement.kaleidoscope_grilling.eat_it_hot.description=Eat a cooked skewer while it is still piping hot.',
  'advancement.kaleidoscope_grilling.neat_and_orderly.title=Neat and Orderly',
  'advancement.kaleidoscope_grilling.neat_and_orderly.description=Place an advanced kitchen rack.',
 ],
 'zh_CN.lang':[
  'advancement.kaleidoscope_grilling.looking_the_part.title=有模有样',
  'advancement.kaleidoscope_grilling.looking_the_part.description=亲手完成第一根串签。',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.title=油光锃亮',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.description=第一次为烧烤架上的烤串刷油。',
  'advancement.kaleidoscope_grilling.three_flavors_base.title=三味打底',
  'advancement.kaleidoscope_grilling.three_flavors_base.description=在调料瓶中集齐三种基础调料。',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.title=瓶中乾坤',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.description=将一个调料瓶装满八份材料。',
  'advancement.kaleidoscope_grilling.eat_it_hot.title=趁热吃！',
  'advancement.kaleidoscope_grilling.eat_it_hot.description=吃下一根仍然带有烟火气的熟烤串。',
  'advancement.kaleidoscope_grilling.neat_and_orderly.title=井井有条',
  'advancement.kaleidoscope_grilling.neat_and_orderly.description=放置一座高级厨具架。',
 ],
 'zh_TW.lang':[
  'advancement.kaleidoscope_grilling.looking_the_part.title=有模有樣',
  'advancement.kaleidoscope_grilling.looking_the_part.description=親手完成第一根串籤。',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.title=油光鋥亮',
  'advancement.kaleidoscope_grilling.gleaming_with_oil.description=第一次為燒烤架上的烤串刷油。',
  'advancement.kaleidoscope_grilling.three_flavors_base.title=三味打底',
  'advancement.kaleidoscope_grilling.three_flavors_base.description=在調料瓶中集齊三種基礎調料。',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.title=瓶中乾坤',
  'advancement.kaleidoscope_grilling.world_in_a_bottle.description=將一個調料瓶裝滿八份材料。',
  'advancement.kaleidoscope_grilling.eat_it_hot.title=趁熱吃！',
  'advancement.kaleidoscope_grilling.eat_it_hot.description=吃下一根仍然帶有煙火氣的熟烤串。',
  'advancement.kaleidoscope_grilling.neat_and_orderly.title=井井有條',
  'advancement.kaleidoscope_grilling.neat_and_orderly.description=放置一座高級廚具架。',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.56 Event Advancement Parity BP'),(rm,'Kaleidoscope Grilling A2.7.56 Event Advancement Parity RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.56 Event Advancement Parity'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_56_Event_Advancement_Parity'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in SCRIPTS:shutil.copy2(DEV/name,scripts/name)

 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 import_anchor="import './a2750_cookery_cuisine_runtime.js';\n"
 import_add=import_anchor+"import {awardLookingThePart,awardGleamingWithOil,awardSeasoningMilestones,awardEatItHot} from './a2756_advancement_event_runtime.js';\n"
 if s.count(import_anchor)!=1:raise RuntimeError('A2.7.56 main import anchor drift')
 if 'a2756_advancement_event_runtime.js' in s:raise RuntimeError('A2.7.56 main already patched')
 s=s.replace(import_anchor,import_add,1)

 old=" message(player,outcome.kind==='fixed'?'§a固定配方完成':outcome.kind==='secret'?'§d秘制串完成':'§e已穿入 '+nextRows.length+'/3');"
 new=" awardLookingThePart(player,outcome);\n"+old
 if s.count(old)!=1:raise RuntimeError('A2.7.56 threading anchor drift')
 s=s.replace(old,new,1)

 old="   if(!commitGrillAndHand(block,state,result.state,player,hand,oil.before,oil.next,oil.mutate)){message(player,'§c刷油交易失敗，油與烤架已嘗試回滾');return}\n"
 new=old+"   awardGleamingWithOil(player);\n"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 Cookery oil award anchor drift')
 s=s.replace(old,new,1)

 old="  if(id&&Object.hasOwn(OIL_TOOLS,id)){const result=brush(state,n,OIL_TOOLS[id]);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}"
 new="  if(id&&Object.hasOwn(OIL_TOOLS,id)){const result=brush(state,n,OIL_TOOLS[id]);if(result.ok){writeState(block,result.state);awardGleamingWithOil(player);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 compatibility oil award anchor drift')
 s=s.replace(old,new,1)

 old="  top.ingredients.push(id);top.kind=hasSeasoningBase(top.ingredients)?'pending':'empty';if(!decrementMain(player))return;writeBottleStack(block,stack);"
 new=old+"awardSeasoningMilestones(player,top.ingredients);"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 seasoning award anchor drift')
 s=s.replace(old,new,1)

 old="function afterCommitted(player,id,meta,active,fullNative){\n applyFixedEffect(player,id);"
 new=old+"\n awardEatItHot(player,id,meta.hot);"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 hot-food award anchor drift')
 s=s.replace(old,new,1)
 main.write_text(s,encoding='utf-8')

 rack=scripts/'a2746_advanced_rack_runtime.js';s=rack.read_text(encoding='utf-8')
 import_anchor="import {readRackPayloadItem,writeRackPayloadItem} from './a2746_rack_item_codec.js';\n"
 import_add=import_anchor+"import {awardNeatAndOrderly} from './a2756_advancement_event_runtime.js';\n"
 if s.count(import_anchor)!=1:raise RuntimeError('A2.7.56 rack import anchor drift')
 if 'awardNeatAndOrderly' in s:raise RuntimeError('A2.7.56 rack already patched')
 s=s.replace(import_anchor,import_add,1)

 old=" const snapshot=event.itemStack.clone(),dimension=event.block.dimension;\n const candidates=rackPlacementCandidates"
 new=" const snapshot=event.itemStack.clone(),dimension=event.block.dimension,player=event.player;\n const candidates=rackPlacementCandidates"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 rack player anchor drift')
 s=s.replace(old,new,1)

 old="   if(block?.typeId===ADVANCED_RACK_BLOCK_ID){restorePlacedRack(block,snapshot);return}"
 new="   if(block?.typeId===ADVANCED_RACK_BLOCK_ID){restorePlacedRack(block,snapshot);awardNeatAndOrderly(player);return}"
 if s.count(old)!=1:raise RuntimeError('A2.7.56 rack placement award anchor drift')
 s=s.replace(old,new,1)
 rack.write_text(s,encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2756-event-advancement-parity.json',{
  'version':'A2.7.56',
  'event_advancements':[
   'looking_the_part','gleaming_with_oil','three_flavors_base',
   'world_in_a_bottle','eat_it_hot','neat_and_orderly'
  ],
  'reuse':{
   'one_shot_adapter':'a2753_advancement_runtime.js',
   'new_listener_count':0,'new_interval_count':0,'duplicate_progression_store':False
  },
  'hooks':{
   'threadCurrent':'looking_the_part',
   'successful_oil_commit':'gleaming_with_oil',
   'seasoning_insert':['three_flavors_base','world_in_a_bottle'],
   'afterCommitted':'eat_it_hot',
   'advanced_rack_placement':'neat_and_orderly'
  },
  'fortress_wart_replacement':{
   'implemented':False,'platform_blocked_without_intrusive_scan':True,
   'reason':'stable Bedrock addon APIs do not expose additive legacy Nether Fortress structure bounding-box patching'
  },
  'native_java_advancement_tree':False,'native_java_toast':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,55]:raise RuntimeError('A2.7.56 must augment published A2.7.55')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.56 event advancement parity complete')

if __name__=='__main__':main()
