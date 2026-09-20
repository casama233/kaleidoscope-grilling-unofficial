import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';
import {RAW_TO_COOKED,FOOD_DATA,PROFILE_BY_ITEM,COOKED_EFFECTS,RAW_NAUSEA,OIL_TOOLS,GRILL_ID,SEASONING_ID,EMPTY_SEASONING_ID,MYSTERIOUS_ID,DARK_ID} from './data.js';
import {initialState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';

const REGISTRY='kaleidoscope_grilling:a2_grills';
const ACTIVE_EATS=new Map();
const SETTLED=new Map();
const MAX_GRILLS=256;

function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function stateKey(block){return 'kaleidoscope_grilling:g_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function inv(block){return block.getComponent('minecraft:inventory')?.container}
function occupied(block){const c=inv(block);if(!c)return 0;let n=0;for(let i=0;i<3;i++)if(c.getItem(i))n++;return n}
function readState(block){
 const raw=world.getDynamicProperty(stateKey(block));if(raw===undefined)return initialState();
 if(typeof raw!=='string')throw new Error('invalid persisted grill state');
 const s=JSON.parse(raw);if(!s||typeof s!=='object')throw new Error('invalid persisted grill state');
 return {...initialState(),...s};
}
function writeState(block,s){world.setDynamicProperty(stateKey(block),JSON.stringify(s))}
function clearState(block){world.setDynamicProperty(stateKey(block))}
function key(block){const p=block.location;return [block.dimension.id,p.x,p.y,p.z].join('|')}
function readRegistry(){try{const raw=world.getDynamicProperty(REGISTRY);return typeof raw==='string'?JSON.parse(raw):[]}catch{return []}}
function saveRegistry(rows){world.setDynamicProperty(REGISTRY,JSON.stringify(rows.slice(0,MAX_GRILLS)))}
function register(block){
 const k=key(block),rows=readRegistry();if(rows.some(x=>x.k===k))return;
 if(rows.length>=MAX_GRILLS)return;
 rows.push({k,d:block.dimension.id,x:block.x,y:block.y,z:block.z});saveRegistry(rows);
}
function isCoreItem(id){return id&&id.startsWith('kaleidoscope_grilling:')}
function isRaw(id){return Object.hasOwn(RAW_TO_COOKED,id)}
function mainContainer(player){return player.getComponent('minecraft:inventory')?.container}
function heldMain(player){return mainContainer(player)?.getItem(player.selectedSlotIndex)}
function setMain(player,stack){mainContainer(player)?.setItem(player.selectedSlotIndex,stack)}
function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function handFor(player,id){
 const m=heldMain(player);if(m?.typeId===id)return {name:'main',stack:m};
 const o=heldOff(player);if(o?.typeId===id)return {name:'off',stack:o};
 return null;
}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
function decrementMain(player){
 if(creative(player))return;
 const s=heldMain(player);if(!s)return;
 if(s.amount<=1)setMain(player,undefined);else{s.amount-=1;setMain(player,s)}
}
function give(player,stack){
 const c=mainContainer(player);if(!c)return;
 const remainder=c.addItem(stack);
 if(remainder)player.dimension.spawnItem(remainder,player.location);
}
function copyOne(stack){return new ItemStack(stack.typeId,1)}
function clearContainer(block){const c=inv(block);if(c)for(let i=0;i<3;i++)c.setItem(i,undefined)}
function resetBlock(block,lit=false){const s=initialState();s.lit=lit;writeState(block,s)}
function cookedStack(raw,state){
 const out=RAW_TO_COOKED[raw.typeId];if(!out)return new ItemStack(MYSTERIOUS_ID,1);
 const stack=new ItemStack(out,1);
 try{stack.setDynamicProperty('kaleidoscope_grilling:hot_ticks',state.heatTicks);stack.setDynamicProperty('kaleidoscope_grilling:seasoned',state.seasoned)}catch{}
 return stack;
}
function outputFor(raw,state,kind){
 if(kind==='raw')return copyOne(raw);
 if(kind==='dark')return new ItemStack(DARK_ID,1);
 if(kind==='mysterious')return new ItemStack(MYSTERIOUS_ID,1);
 return cookedStack(raw,state);
}
function extract(block,player,all=false){
 let state=readState(block);if(!canExtract(state))return 0;
 const c=inv(block);if(!c)return 0;let count=0;
 for(let i=0;i<3;i++){
  const raw=c.getItem(i);if(!raw)continue;
  const kind=outputKind(state);give(player,outputFor(raw,state,kind));c.setItem(i,undefined);count++;
  if(!all)break;
 }
 if(occupied(block)===0)resetBlock(block,state.lit);
 if(count){try{block.dimension.playSound('random.pop',block.location)}catch{}}
 return count;
}
function customBreak(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;
 const state=readState(block),kind=breakDisposition(state),c=inv(block);
 if(c)for(let i=0;i<3;i++){const raw=c.getItem(i);if(raw)player.dimension.spawnItem(outputFor(raw,state,kind),{x:block.x+.5,y:block.y+.4,z:block.z+.5})}
 clearContainer(block);clearState(block);block.setType('minecraft:air');
 if(!creative(player))player.dimension.spawnItem(new ItemStack(GRILL_ID,1),{x:block.x+.5,y:block.y+.3,z:block.z+.5});
}
function seasoningUse(player){
 const stack=heldMain(player);if(!stack||stack.typeId!==SEASONING_ID)return;
 let uses=0;try{uses=Number(stack.getDynamicProperty('kaleidoscope_grilling:uses')??0)}catch{}
 uses++;
 if(uses>=16)setMain(player,new ItemStack(EMPTY_SEASONING_ID,1));
 else{try{stack.setDynamicProperty('kaleidoscope_grilling:uses',uses)}catch{}setMain(player,stack)}
}
function handleGrill(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;
 register(block);let state=readState(block);const held=heldMain(player),id=held?.typeId;
 if(id==='minecraft:flint_and_steel'){
  if(!state.lit){state=light(state,true);writeState(block,state);try{block.dimension.playSound('fire.ignite',block.location)}catch{};message(player,'§6烤爐已點火')}
  return;
 }
 if(id&&Object.hasOwn(OIL_TOOLS,id)){
  const result=brush(state,occupied(block),OIL_TOOLS[id]);
  if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.main',{blendOutTime:.12})}catch{};message(player,'§e刷油完成，開始翻面')}
  else message(player,state.lit?'§7現在不能刷油':'§c烤爐尚未點火');
  return;
 }
 if(id===SEASONING_ID){
  const result=season(state,occupied(block));
  if(result.ok){writeState(block,result.state);seasoningUse(player);try{player.playAnimation('animation.kg_imm.player.season.main',{blendOutTime:.12})}catch{};message(player,'§a調味完成，可以取串')}
  else message(player,'§7現在不能撒料');
  return;
 }
 if(id&&isRaw(id)){
  if(!state.lit){message(player,'§c需要先點火');return}
  if(!canInsert(state,occupied(block))){message(player,'§7烤爐現在不能再放入生串');return}
  const c=inv(block),slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;
  c.setItem(slot,new ItemStack(id,1));decrementMain(player);message(player,'§a已放入烤串 '+(slot+1)+'/3');return;
 }
 if(id){message(player,'§7這個物品不能用在目前的烤爐階段');return}
 const n=occupied(block);
 if(state.phase===1){
  const r=flip(state);
  if(r.ok){writeState(block,r.state);try{player.playAnimation('animation.kg_imm.player.reach.main',{blendOutTime:.1});block.dimension.playSound('kg_imm.grill_flip',block.location)}catch{};message(player,'§e翻面 '+r.state.flips+'/4')}
  else message(player,'§7翻面冷卻中');
  return;
 }
 if(state.phase===0&&n>0){message(player,'§e還需要刷油');return}
 if(state.phase===2&&!state.seasoned){message(player,'§e還需要撒料');return}
 if(canExtract(state)){const got=extract(block,player,player.isSneaking);if(got)message(player,'§a取出 '+got+' 串');return}
}
function applyFoodEffect(player,id){
 const d=FOOD_DATA[id];if(!d)return;
 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{}
 const e=COOKED_EFFECTS[id];
 if(e?.effect?.startsWith('minecraft:'))try{player.addEffect(e.effect.split(':')[1],Math.max(1,e.seconds*20),{showParticles:true})}catch{}
 if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{}
 if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 if(id==='kaleidoscope_grilling:grilled_golden_skewer'){
  player.setDynamicProperty('kaleidoscope_grilling:invincible_until',system.currentTick+200);
  try{player.dimension.playSound('beacon.power',player.location)}catch{}
 }
 if(e&&e.effect&&!e.effect.startsWith('minecraft:')&&e.effect!=='kaleidoscope_grilling:invincible')message(player,'§8Cookery 專屬效果待 A2.x 對接：'+e.effect);
}
function hungerSettle(player,id){
 const d=FOOD_DATA[id];if(!d)return false;
 const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!h||!sat)return false;
 const hunger=Math.min(h.effectiveMax,h.currentValue+d.nutrition);h.setCurrentValue(hunger);
 sat.setCurrentValue(Math.min(hunger,sat.currentValue+d.nutrition*d.saturation*2));
 const active=ACTIVE_EATS.get(player.id),hand=active?.hand??'main';
 let stack=hand==='off'?heldOff(player):heldMain(player);
 if(!stack||stack.typeId!==id)return false;
 if(stack.amount<=1){if(hand==='off')setOff(player,undefined);else setMain(player,undefined)}
 else{stack.amount-=1;if(hand==='off')setOff(player,stack);else setMain(player,stack)}
 applyFoodEffect(player,id);return true;
}
function resolvedProfile(profile){return profile==='THREE_RANDOM'?(Math.random()<.5?'THREE':'THREE_ALT'):profile}
function profileDuration(profile){return profile==='THREE'?100:90}
world.afterEvents.itemStartUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(!FOOD_DATA[id])return;
 const hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(PROFILE_BY_ITEM[id]??'THREE');
 ACTIVE_EATS.set(e.source.id,{id,start:system.currentTick,profile,hand});
 try{e.source.playAnimation('animation.kg_imm.player.eat_'+profile.toLowerCase()+'.'+hand,{blendOutTime:.12})}catch{}
});
world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(!FOOD_DATA[id])return;
 SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);applyFoodEffect(e.source,id);
});
world.afterEvents.itemStopUse.subscribe(e=>{
 const a=ACTIVE_EATS.get(e.source.id);if(!a)return;ACTIVE_EATS.delete(e.source.id);
 if(SETTLED.get(e.source.id)===system.currentTick)return;
 const used=system.currentTick-a.start;
 if(used>=25&&used<profileDuration(a.profile)){if(hungerSettle(e.source,a.id))message(e.source,'§a在1.25秒檢查點完成進食')}
 try{e.source.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}
});
world.beforeEvents.entityHurt.subscribe(e=>{
 const until=e.hurtEntity.getDynamicProperty?.('kaleidoscope_grilling:invincible_until');
 if(typeof until==='number'&&until>system.currentTick){e.cancel=true;system.run(()=>{try{e.hurtEntity.dimension.playSound('random.shield_block',e.hurtEntity.location)}catch{}})}
});
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(e.block.typeId!==GRILL_ID)return;e.cancel=true;
 const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>handleGrill(dim.getBlock(loc),p));
});
world.afterEvents.playerPlaceBlock.subscribe(e=>{if(e.block.typeId===GRILL_ID){register(e.block);resetBlock(e.block,false)}});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.block.typeId!==GRILL_ID)return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>customBreak(dim.getBlock(loc),p));
});
system.runInterval(()=>{
 const rows=readRegistry(),keep=[];
 for(const row of rows){
  try{
   const block=world.getDimension(row.d).getBlock({x:row.x,y:row.y,z:row.z});
   if(!block||block.typeId!==GRILL_ID)continue;keep.push(row);
   let state=readState(block),before=state.phase;const result=tickState(state,occupied(block),1);state=result.state;
   if(result.events.some(x=>x.kind==='burn_to_charcoal')){
    const count=1+Math.floor(Math.random()*2);clearContainer(block);block.dimension.spawnItem(new ItemStack('minecraft:charcoal',count),{x:block.x+.5,y:block.y+.4,z:block.z+.5});writeState(block,state);continue;
   }
   if(before!==state.phase)try{block.dimension.playSound('fire.fire',block.location)}catch{}
   writeState(block,state);
   if(state.lit&&system.currentTick%4===0){
    const p={x:block.x+.5+(Math.random()-.5)*.45,y:block.y+.35,z:block.z+.5+(Math.random()-.5)*.45};
    if(Math.random()<.35)block.dimension.spawnParticle('minecraft:basic_smoke_particle',p);
    if(Math.random()<.12)block.dimension.spawnParticle('minecraft:basic_flame_particle',p);
   }
  }catch{}
 }
 if(keep.length!==rows.length)saveRegistry(keep);
},1);
