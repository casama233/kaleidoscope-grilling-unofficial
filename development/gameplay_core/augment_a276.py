from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.6 patch anchor missing: '+label)
 return s.replace(old,new,1)
def replace_between(s,start,end,new,label):
 i=s.find(start);j=s.find(end,i+len(start))
 if i<0 or j<0:raise RuntimeError('A2.7.6 range anchor missing: '+label)
 return s[:i]+new+s[j:]

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.6 Grill Intent/Hand Parity BP'),(rm,'Kaleidoscope Grilling A2.7.6 Grill Intent/Hand Parity RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.6 Grill Intent Hand Parity';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_6_Grill_Intent';write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/'a276_grill_intent_core.js',BP/'scripts/a276_grill_intent_core.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')

 anchor="import {isExtinguishTool,isInitialBlockPress,nextDurability} from './a275_grill_input_core.js';"
 s=replace_once(s,anchor,anchor+"\nimport {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';",'intent helper import')

 old="""function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function handFor(player,id){const m=heldMain(player);if(m?.typeId===id)return {name:'main',stack:m};const o=heldOff(player);if(o?.typeId===id)return {name:'off',stack:o};return null}
function setHand(player,hand,stack){if(hand==='off')return setOff(player,stack);return setMain(player,stack)}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
function decrementMain(player,count=1){if(creative(player))return true;const s=heldMain(player);if(!s||s.amount<count)return false;if(s.amount===count)setMain(player,undefined);else{s.amount-=count;setMain(player,s)}return true}
function damageMainTool(player,amount=1){
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
 new="""function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function heldByHand(player,hand){return hand==='off'?heldOff(player):heldMain(player)}
function handFor(player,id){const m=heldMain(player);if(m?.typeId===id)return {name:'main',stack:m};const o=heldOff(player);if(o?.typeId===id)return {name:'off',stack:o};return null}
function setHand(player,hand,stack){if(hand==='off')return setOff(player,stack);return setMain(player,stack)}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
function decrementHand(player,hand,count=1){
 if(creative(player))return true;const s=heldByHand(player,hand);if(!s||s.amount<count)return false;
 if(s.amount===count)setHand(player,hand,undefined);else{s.amount-=count;setHand(player,hand,s)}return true;
}
function decrementMain(player,count=1){return decrementHand(player,'main',count)}
function damageHandTool(player,hand,amount=1){
 if(creative(player))return false;
 const stack=heldByHand(player,hand);if(!stack)return false;
 try{
  const durability=stack.getComponent('minecraft:durability');if(!durability)return false;
  const next=nextDurability(durability.damage,durability.maxDurability,amount,!!durability.unbreakable);
  if(next.broken){setHand(player,hand,undefined);try{player.playSound('random.break',{volume:.8,pitch:1})}catch{};return true}
  if(next.damage!==durability.damage){durability.damage=next.damage;setHand(player,hand,stack)}
  return false;
 }catch{return false}
}"""
 s=replace_once(s,old,new,'generic hand inventory helpers')

 anchor="""function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}
 for(const id of ids)try{const value=stack.getDynamicProperty(id);if(['string','number','boolean'].includes(typeof value))out[id]=value;else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z}}catch{}
 return out;
}"""
 extra=anchor+"""
function stackIntentSignature(stack){
 if(!stack)return null;
 const raw=primitiveProps(stack),props=Object.fromEntries(Object.keys(raw).sort().map(k=>[k,raw[k]]));
 let lore=[];try{lore=stack.getLore()}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 let damage=null;try{damage=Number(stack.getComponent('minecraft:durability')?.damage??0)}catch{}
 return JSON.stringify({id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props,damage});
}
function stackIntentDescriptor(stack){
 return stack?{empty:false,id:stack.typeId,sig:stackIntentSignature(stack)}:{empty:true,id:null,sig:null};
}
function captureGrillIntent(player,eventStack){
 const e=stackIntentDescriptor(eventStack),m=stackIntentDescriptor(heldMain(player)),o=stackIntentDescriptor(heldOff(player));
 const hand=chooseInteractionHand(e,m,o),sig=hand==='off'?o.sig:m.sig;
 return makeIntent(hand,sig,player.selectedSlotIndex);
}
function grillIntentStillCurrent(player,intent){
 return intentMatches(intent,stackIntentSignature(heldMain(player)),stackIntentSignature(heldOff(player)),player.selectedSlotIndex);
}"""
 s=replace_once(s,anchor,extra,'deferred intent snapshot')

 old="""function consumeCookeryOil(player,needed){
 const stack=heldMain(player);if(stack?.typeId!==COOKERY_FILLED)return {ok:false,reason:'not_pot'};
 const count=cookeryOilCount(stack);if(count<needed)return {ok:false,reason:'insufficient',count};
 const type=cookeryOilType(stack);if(creative(player))return {ok:true,heat:heatForOil(type),remaining:count};
 const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1),cap=type?FLUID_CAPACITY:256;
 if(remaining>0){try{next.setLore(['§7Oil: '+remaining+'/'+cap]);next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type)next.setDynamicProperty('kaleidoscope_grilling:oil_type',type)}catch{}}
 setMain(player,next);return {ok:true,heat:heatForOil(type),remaining};
}
function consumeSeasoningBottle(player,needed){
 const stack=heldMain(player);if(stack?.typeId!==SEASONING_ID)return {ok:false,reason:'not_seasoning'};
 const uses=getUses(stack),remaining=16-uses;if(remaining<needed)return {ok:false,reason:'insufficient',remaining};
 const ingredients=readSeasonings(stack);if(creative(player))return {ok:true,ingredients,uses};
 const next=uses+needed;if(next>=16)setMain(player,new ItemStack(EMPTY_SEASONING_ID,1));
 else{setUses(stack,next);try{stack.setLore(['§7Uses: '+(16-next)+'/16'])}catch{}setMain(player,stack)}
 return {ok:true,ingredients,uses:next};
}"""
 new="""function consumeCookeryOil(player,hand,needed){
 const stack=heldByHand(player,hand);if(stack?.typeId!==COOKERY_FILLED)return {ok:false,reason:'not_pot'};
 const count=cookeryOilCount(stack);if(count<needed)return {ok:false,reason:'insufficient',count};
 const type=cookeryOilType(stack);if(creative(player))return {ok:true,heat:heatForOil(type),remaining:count};
 const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1),cap=type?FLUID_CAPACITY:256;
 if(remaining>0){try{next.setLore(['§7Oil: '+remaining+'/'+cap]);next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type)next.setDynamicProperty('kaleidoscope_grilling:oil_type',type)}catch{}}
 setHand(player,hand,next);return {ok:true,heat:heatForOil(type),remaining};
}
function consumeSeasoningBottle(player,hand,needed){
 const stack=heldByHand(player,hand);if(stack?.typeId!==SEASONING_ID)return {ok:false,reason:'not_seasoning'};
 const uses=getUses(stack),remaining=16-uses;if(remaining<needed)return {ok:false,reason:'insufficient',remaining};
 const ingredients=readSeasonings(stack);if(creative(player))return {ok:true,ingredients,uses};
 const next=uses+needed;if(next>=16)setHand(player,hand,new ItemStack(EMPTY_SEASONING_ID,1));
 else{setUses(stack,next);try{stack.setLore(['§7Uses: '+(16-next)+'/16'])}catch{}setHand(player,hand,stack)}
 return {ok:true,ingredients,uses:next};
}"""
 s=replace_once(s,old,new,'hand-aware resources')

 new_handle="""function handleGrill(block,player,hand='main'){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;register(block);let state=readState(block);const held=heldByHand(player,hand),id=held?.typeId,n=occupied(block);
 if(id==='minecraft:flint_and_steel'){
  if(!state.lit){state=light(state,true);writeState(block,state);damageHandTool(player,hand,1);try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')}
  return
 }
 if(isExtinguishTool(id)&&state.lit){
  state=light(state,false);writeState(block,state);try{block.dimension.playSound('random.fizz',block.location)}catch{}message(player,'§7烤爐已熄滅');return
 }
 if(id===COOKERY_FILLED){
  if(state.phase!==0||n<1){message(player,'§7現在不能刷油');return}
  const oil=consumeCookeryOil(player,hand,n);if(!oil.ok){message(player,oil.reason==='insufficient'?'§c油量不足：需要 '+n+'，目前 '+oil.count:'§7需要森羅物語裝油的油壺');return}
  const result=brush(state,n,oil.heat);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}message(player,'§e刷油完成，消耗 '+(creative(player)?0:n)+' 點油')}return;
 }
 if(id&&Object.hasOwn(OIL_TOOLS,id)){const result=brush(state,n,OIL_TOOLS[id]);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}message(player,'§8相容刷具：已刷油；正式流程請使用 Cookery 油壺')}return}
 if(id===SEASONING_ID){
  if(state.phase!==2||state.seasoned||n<1){message(player,'§7現在不能撒料');return}
  const bottle=consumeSeasoningBottle(player,hand,n);if(!bottle.ok){message(player,bottle.reason==='insufficient'?'§c調料不足：爐上 '+n+' 串需要 '+n+' 次，剩 '+bottle.remaining+' 次':'§7需要完成的調料瓶');return}
  const result=season(state,n,bottle.ingredients);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.season.'+hand,{blendOutTime:.12})}catch{}message(player,'§a調味完成，消耗 '+(creative(player)?0:n)+' 次')}return;
 }
 if(id&&(Object.hasOwn(RAW_TO_COOKED,id)||(id===SECRET_ID&&!isSecretCooked(held)&&readSkewerRows(held).length===3))){
  if(!state.lit){message(player,'§c需要先點火');return}if(!canInsert(state,n)){message(player,'§7烤爐現在不能再放入生串');return}
  const c=inv(block),slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;
  c.setItem(slot,copyOne(held));
  if(!decrementHand(player,hand)){c.setItem(slot,undefined);message(player,'§c手中物品已變更，插串已取消');return}
  message(player,'§a已放入烤串 '+(slot+1)+'/3');return
 }
 if(id){message(player,'§7這個物品不能用在目前的烤爐階段');return}
 if(state.phase===1){const r=flip(state);if(r.ok){writeState(block,r.state);try{player.playAnimation('animation.kg_imm.player.reach.'+hand,{blendOutTime:.1});block.dimension.playSound('kg_imm.grill_flip',block.location)}catch{}message(player,'§e翻面 '+r.state.flips+'/4')}else message(player,'§7翻面冷卻中');return}
 if(state.phase===0&&n>0){message(player,'§e還需要刷油');return}if(state.phase===2&&!state.seasoned){message(player,'§e還需要撒料');return}
 if(canExtract(state)){const got=extract(block,player,player.isSneaking);if(got)message(player,'§a取出 '+got+' 串')}
}
"""
 s=replace_between(s,'function handleGrill(block,player){','function readBottleStack(block){',new_handle,'hand-aware handleGrill')

 old_event="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
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
 new_event="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));
 if(skewerInput){e.cancel=true;if(isInitialBlockPress(e.isFirstEvent))scheduleSkewerAction(e.player,skewerInput);return}
 const grillTarget=e.block.typeId===GRILL_ID,customTarget=grillTarget||isSeasoningBlock(e.block.typeId);
 const sortTarget=e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId);
 if(!isInitialBlockPress(e.isFirstEvent)){if(customTarget||sortTarget)e.cancel=true;return}
 if(sortTarget){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;const r=compactSkewerContainer(c,false);message(p,r.changed?'§b已整理串類：熱度差≤5分鐘的熱串按數量加權合併':'§7沒有可整理的串類')});return;
 }
 if(!customTarget)return;
 e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension,intent=grillTarget?captureGrillIntent(p,e.itemStack):null;
 system.run(()=>{
  const block=dim.getBlock(loc);
  if(block?.typeId===GRILL_ID){
   if(!grillIntentStillCurrent(p,intent)){message(p,'§7操作已取消：互動後手持物品已改變');return}
   handleGrill(block,p,intent.hand);
  }else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p);
 });
});"""
 s=replace_once(s,old_event,new_event,'deferred grill intent validation')

 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a276-grill-intent-hand.json',{
  'version':'A2.7.6',
  'scope':'deferred grill intent stability and Java InteractionHand parity only; no new content',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'fixes':{
   'deferred_toctou':{
    'status':'fixed',
    'before':'system.run callback re-read whatever happened to be in main hand',
    'after':'capture used-hand signature at before-event time; abort if selected main slot or used stack changes before deferred callback'
   },
   'interaction_hand':{
    'status':'ported_with_ambiguity_fallback',
    'java':'GrillBlock.use receives InteractionHand and consumes/animates that hand',
    'bedrock':'infer used hand from PlayerInteractWithBlockBeforeEvent.itemStack versus main/offhand signatures; identical ambiguous stacks deterministically fall back to main'
   },
   'hand_transactions':{
    'status':'fixed',
    'covers':['flint_and_steel durability','shovel extinguish','Cookery oil consumption','compat oil brush','seasoning use','raw skewer insertion','flip animation']
   },
   'insert_rollback':{
    'status':'fixed',
    'behavior':'if held-stack decrement unexpectedly fails after slot insertion, inserted slot is cleared immediately'
   }
  },
  'known_boundaries':[
   'Bedrock stable event has no explicit InteractionHand field; if both hands contain byte-equivalent stacks, hand inference falls back to main.',
   'Seasoning-bottle world block interaction remains main-hand-oriented and is outside this grill-only slice.',
   'Minecraft/BDS engine acceptance remains required.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,5]:raise RuntimeError('A2.7.6 must augment verified A2.7.5')
 patch_versions();patch_runtime();report();print('A2.7.6 grill intent/hand parity complete')
if __name__=='__main__':main()
