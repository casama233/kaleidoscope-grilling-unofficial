from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,5]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.5 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.5 Grill Input Hardening BP'),(rm,'Kaleidoscope Grilling A2.7.5 Grill Input Hardening RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.5 Grill Input Hardening';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_5_Grill_Input';write(P/'config.json',cfg)

def patch_core():
 path=BP/'scripts/core_logic.js';s=path.read_text(encoding='utf-8')
 old="if(!validState(state)||state.phase!==0||occupied<1||!state.lit||!Number.isInteger(heatTicks)||heatTicks<1)return {ok:false,state};"
 new="if(!validState(state)||state.phase!==0||occupied<1||!Number.isInteger(heatTicks)||heatTicks<1)return {ok:false,state};"
 s=replace_once(s,old,new,'Java brushOil does not require lit')
 path.write_text(s,encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a275_grill_input_core.js',BP/'scripts/a275_grill_input_core.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')

 anchor="import './a272_cookery_processing_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport {isExtinguishTool,isInitialBlockPress,nextDurability} from './a275_grill_input_core.js';",'input helper import')

 old="function decrementMain(player,count=1){if(creative(player))return true;const s=heldMain(player);if(!s||s.amount<count)return false;if(s.amount===count)setMain(player,undefined);else{s.amount-=count;setMain(player,s)}return true}"
 new=old+"""\nfunction damageMainTool(player,amount=1){
 if(creative(player))return false;
 const stack=heldMain(player);if(!stack)return false;
 try{
  const durability=stack.getComponent('minecraft:durability');if(!durability)return false;
  const next=nextDurability(durability.damage,durability.maxDurability,amount,!!durability.unbreakable);
  if(next.broken){setMain(player,undefined);try{player.playSound('random.break',{volume:.8,pitch:1})}catch{};return true}
  if(next.damage!==durability.damage){durability.damage=next.damage;setMain(player,stack)}
  return false;
 }catch{return false}
}"""
 s=replace_once(s,old,new,'tool durability helper')

 old="if(id==='minecraft:flint_and_steel'){if(!state.lit){state=light(state,true);writeState(block,state);try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')}return}"
 new="""if(id==='minecraft:flint_and_steel'){
  if(!state.lit){state=light(state,true);writeState(block,state);damageMainTool(player,1);try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')}
  return
 }
 if(isExtinguishTool(id)&&state.lit){
  state=light(state,false);writeState(block,state);try{block.dimension.playSound('random.fizz',block.location)}catch{}message(player,'§7烤爐已熄滅');return
 }"""
 s=replace_once(s,old,new,'ignite durability and extinguish')

 old="if(state.phase!==0||n<1||!state.lit){message(player,state.lit?'§7現在不能刷油':'§c烤爐尚未點火');return}"
 new="if(state.phase!==0||n<1){message(player,'§7現在不能刷油');return}"
 s=replace_once(s,old,new,'oil before ignition')

 old="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));if(skewerInput){e.cancel=true;scheduleSkewerAction(e.player,skewerInput);return}
 if(e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;const r=compactSkewerContainer(c,false);message(p,r.changed?'§b已整理串類：熱度差≤5分鐘的熱串按數量加權合併':'§7沒有可整理的串類')});return;
 }
 if(e.block.typeId!==GRILL_ID&&!isSeasoningBlock(e.block.typeId))return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)});
});"""
 new="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));
 if(skewerInput){e.cancel=true;if(isInitialBlockPress(e.isFirstEvent))scheduleSkewerAction(e.player,skewerInput);return}
 const customTarget=e.block.typeId===GRILL_ID||isSeasoningBlock(e.block.typeId);
 const sortTarget=e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId);
 if(!isInitialBlockPress(e.isFirstEvent)){if(customTarget||sortTarget)e.cancel=true;return}
 if(sortTarget){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;const r=compactSkewerContainer(c,false);message(p,r.changed?'§b已整理串類：熱度差≤5分鐘的熱串按數量加權合併':'§7沒有可整理的串類')});return;
 }
 if(!customTarget)return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)});
});"""
 s=replace_once(s,old,new,'first-event gating')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a275-grill-input-hardening.json',{
  'version':'A2.7.5',
  'scope':'grill input hardening only; no new food/recipe content',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'bedrock_api':'@minecraft/server 2.9.0',
  'fixes':{
   'held_block_interaction_repeat':{
    'status':'fixed',
    'mechanism':'PlayerInteractWithBlockBeforeEvent.isFirstEvent; repeated hold events are cancelled for Grilling custom targets and threading/sort actions'
   },
   'extinguish':{
    'status':'ported',
    'java_selector':'#kaleidoscope_cookery:extinguish_stove = #minecraft:shovels plus Cookery kitchen shovel',
    'bedrock_ids':['minecraft:wooden_shovel','minecraft:stone_shovel','minecraft:iron_shovel','minecraft:golden_shovel','minecraft:diamond_shovel','minecraft:netherite_shovel','kaleidoscope_cookery:kitchen_shovel','kaleidoscope_cookery:oiled_kitchen_shovel']
   },
   'oil_before_ignition':{
    'status':'fixed',
    'java_behavior':'GrillAutomationApi.brushOil checks phase/occupancy/oil but not LIT'
   },
   'flint_and_steel_durability':{
    'status':'fixed',
    'java_behavior':'ignite hurts flint and steel by 1 outside creative',
    'bedrock_component':'minecraft:durability'
   }
  },
  'known_boundaries':[
   'Cookery Bedrock oiled-kitchen-shovel internal oil metadata is not mutated because no public host API for that private state is used; both visible shovel ids can extinguish.',
   'PlayerInteractWithEntityBeforeEvent has no isFirstEvent property in stable docs, so this slice only hardens repeated block interactions.',
   'Minecraft/BDS engine acceptance remains required.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,4]:raise RuntimeError('A2.7.5 must augment verified A2.7.4')
 patch_versions();patch_core();patch_runtime();report();print('A2.7.5 grill input hardening complete')
if __name__=='__main__':main()
