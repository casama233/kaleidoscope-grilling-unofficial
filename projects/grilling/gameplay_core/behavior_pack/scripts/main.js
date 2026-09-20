import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';
import {RAW_TO_COOKED,FOOD_DATA,PROFILE_BY_ITEM,COOKED_EFFECTS,RAW_NAUSEA,OIL_TOOLS,GRILL_ID,SEASONING_ID,EMPTY_SEASONING_ID,MYSTERIOUS_ID,DARK_ID} from './data.js';
import {initialState,normalizeState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';
import {mergeIntoContainer,compactSkewerContainer} from './a23_hot_runtime.js';
import {UNFINISHED_ID,SECRET_ID,readIngredients,isSecretCooked,canDisassemble,createThreaded,cookSecret,copySkewerProperties,disassemblyItems,secretFoodStats,isThreadTarget,canAppend} from './a24_skewering.js';
import './a23_oil_world.js';

const REGISTRY='kaleidoscope_grilling:a2_grills';
const ACTIVE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();
const MAX_GRILLS=256;
const COOKERY_POT='kaleidoscope_cookery:oil_pot',COOKERY_FILLED='kaleidoscope_cookery:oil_pot_filled',COOKERY_OIL_KEY='kc_oil_count';
const PENDING_SEASONING='kaleidoscope_grilling:pending_seasoning',SEASONING_BLOCK='kaleidoscope_grilling:seasoning_bottle_1';
const SEASONING_BLOCKS=new Set(['kaleidoscope_grilling:seasoning_bottle','kaleidoscope_grilling:seasoning_bottle_1','kaleidoscope_grilling:seasoning_bottle_2','kaleidoscope_grilling:seasoning_bottle_3','kaleidoscope_grilling:seasoning_bottle_4']);
const SEASON_LIST_KEY='kaleidoscope_grilling:seasonings',SEASON_USES_KEY='kaleidoscope_grilling:uses',SEASON_VARIANT_KEY='kaleidoscope_grilling:variant';
const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until',FX_KEY='kaleidoscope_grilling:a21_fx';
const BASE_SEASONINGS=new Set(['kaleidoscope_grilling:green_chili_powder','kaleidoscope_grilling:sichuan_pepper','kaleidoscope_grilling:onion_powder']);
const SEASONING_KINDS=Object.freeze({
 'minecraft:redstone':'speed','minecraft:gunpowder':'strength',
 'kaleidoscope_grilling:houttuynia_powder':'duration','kaleidoscope_grilling:totem_powder':'totem',
 'kaleidoscope_grilling:dragon_egg_powder':'vitality','kaleidoscope_grilling:sichuan_pepper':'numbness',
 'kaleidoscope_grilling:green_chili_powder':'base','kaleidoscope_grilling:onion_powder':'base'
});
const HEAT_BLOCKS=new Set(['minecraft:fire','minecraft:soul_fire','minecraft:lava','minecraft:campfire','minecraft:soul_campfire','minecraft:magma']);
const TUNDRA_BLOCKS=new Set(['minecraft:snow','minecraft:snow_layer','minecraft:snow_block','minecraft:powder_snow','minecraft:ice','minecraft:packed_ice','minecraft:blue_ice','minecraft:frosted_ice']);
const DANGEROUS_FOODS=new Set(['minecraft:rotten_flesh','minecraft:chicken','minecraft:poisonous_potato','minecraft:pufferfish','minecraft:spider_eye']);
const BITE_TIMES=Object.freeze({
 ONE:[1.16667,3.08333],TWO:[0.95833,4.0],THREE:[0.95833,2.33333,3.54167],THREE_ALT:[0.95833,2.16667,3.5],FOUR:[0.95833,2.33333,3.45833,4.08333]
});
const NUMB_VISUAL=new Set(),DRAGON_REPLAY=new Set();
const STORAGE_SORT_BLOCKS=new Set(['minecraft:chest','minecraft:trapped_chest','minecraft:barrel']);
const DRAGON_POOL_KEY='kaleidoscope_grilling:dragon_pool';
const OIL_TYPES=Object.freeze({canola:{heatTicks:1200},secret_chili:{heatTicks:12000},premium_chili:{heatTicks:24000}});
function isSeasoningBlock(id){return SEASONING_BLOCKS.has(id)}
function soundFor(profile){return profile==='ONE'?'one_skewer_eat':profile==='TWO'?'two_skewer_eat':profile==='FOUR'?'four_skewer_eat':'three_skewer_eat'}
function stopEatSound(player,profile){try{player.runCommand('stopsound @s kg_imm.'+soundFor(profile))}catch{}}
function spawnBiteCrumbs(player){
 try{
  const h=player.getHeadLocation(),v=player.getViewDirection();
  for(let i=0;i<5;i++)player.dimension.spawnParticle('kaleidoscope_grilling:skewer_crumb',{x:h.x+v.x*.32+(Math.random()-.5)*.14,y:h.y-.08+(Math.random()-.5)*.12,z:h.z+v.z*.32+(Math.random()-.5)*.14});
 }catch{}
}
function advanceBites(player,a){
 const elapsed=(system.currentTick-a.start)/20,times=a.biteTimes??[];
 while((a.nextBite??0)<times.length&&elapsed+1e-6>=times[a.nextBite]){spawnBiteCrumbs(player);a.nextBite++;try{player.playSound('random.eat',{volume:.35,pitch:1.0})}catch{}}
}


function now(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function stateKey(block){return 'kaleidoscope_grilling:g_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function seasoningBlockKey(block){return 'kaleidoscope_grilling:sb_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function inv(block){return block.getComponent('minecraft:inventory')?.container}
function occupied(block){const c=inv(block);if(!c)return 0;let n=0;for(let i=0;i<3;i++)if(c.getItem(i))n++;return n}
function readState(block){
 const raw=world.getDynamicProperty(stateKey(block));if(raw===undefined)return initialState();
 if(typeof raw!=='string')throw new Error('invalid persisted grill state');
 return normalizeState(JSON.parse(raw));
}
function syncGrillPermutation(block,state){
 try{
  let perm=block.permutation,below=block.below(),legged=!(below?.isSolid??false),lit=!!state.lit;
  if(perm.getState('kaleidoscope_grilling:legged')!==legged)perm=perm.withState('kaleidoscope_grilling:legged',legged);
  if(perm.getState('kaleidoscope_grilling:lit')!==lit)perm=perm.withState('kaleidoscope_grilling:lit',lit);
  block.setPermutation(perm);
 }catch{}
}
function writeState(block,s){const state=normalizeState(s);world.setDynamicProperty(stateKey(block),JSON.stringify(state));syncGrillPermutation(block,state)}
function clearState(block){world.setDynamicProperty(stateKey(block))}
function key(block){const p=block.location;return [block.dimension.id,p.x,p.y,p.z].join('|')}
function readRegistry(){try{const raw=world.getDynamicProperty(REGISTRY);return typeof raw==='string'?JSON.parse(raw):[]}catch{return []}}
function saveRegistry(rows){world.setDynamicProperty(REGISTRY,JSON.stringify(rows.slice(0,MAX_GRILLS)))}
function register(block){const k=key(block),rows=readRegistry();if(rows.some(x=>x.k===k)||rows.length>=MAX_GRILLS)return;rows.push({k,d:block.dimension.id,x:block.x,y:block.y,z:block.z});saveRegistry(rows)}
function mainContainer(player){return player.getComponent('minecraft:inventory')?.container}
function heldMain(player){return mainContainer(player)?.getItem(player.selectedSlotIndex)}
function setMain(player,stack){mainContainer(player)?.setItem(player.selectedSlotIndex,stack)}
function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function handFor(player,id){const m=heldMain(player);if(m?.typeId===id)return {name:'main',stack:m};const o=heldOff(player);if(o?.typeId===id)return {name:'off',stack:o};return null}
function setHand(player,hand,stack){if(hand==='off')return setOff(player,stack);return setMain(player,stack)}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
function decrementMain(player,count=1){if(creative(player))return true;const s=heldMain(player);if(!s||s.amount<count)return false;if(s.amount===count)setMain(player,undefined);else{s.amount-=count;setMain(player,s)}return true}
function give(player,stack){const c=mainContainer(player);if(!c)return;const rem=mergeIntoContainer(c,stack);if(rem)player.dimension.spawnItem(rem,player.location)}
function copyOne(stack){const out=stack.clone();out.amount=1;return out}
function clearContainer(block){const c=inv(block);if(c)for(let i=0;i<3;i++)c.setItem(i,undefined)}
function resetBlock(block,lit=false){const s=initialState();s.lit=lit;writeState(block,s)}
function parseList(raw){if(typeof raw!=='string')return [];try{const v=JSON.parse(raw);return Array.isArray(v)?v.filter(x=>typeof x==='string').slice(0,8):[]}catch{return []}}
function readSeasonings(stack){try{return parseList(stack?.getDynamicProperty(SEASON_LIST_KEY))}catch{return []}}
function setSeasonings(stack,list){try{stack.setDynamicProperty(SEASON_LIST_KEY,JSON.stringify(list.slice(0,8)))}catch{}return stack}
function hasSeasoningBase(list){return [...BASE_SEASONINGS].every(x=>list.includes(x))}
function getUses(stack){try{return Math.max(0,Math.min(16,Number(stack?.getDynamicProperty(SEASON_USES_KEY)??0)|0))}catch{return 0}}
function setUses(stack,n){try{stack.setDynamicProperty(SEASON_USES_KEY,Math.max(0,Math.min(16,n|0)))}catch{}return stack}
function bucketHot(until){return until-(((until%100)+100)%100)}
function setHot(stack,ticks){if(ticks<=0)return stack;try{stack.setDynamicProperty(HOT_UNTIL_KEY,bucketHot(now()+ticks))}catch{}return stack}
function hotUntil(stack){try{return Number(stack?.getDynamicProperty(HOT_UNTIL_KEY)??0)}catch{return 0}}
function isHot(stack){return hotUntil(stack)>now()}
function refreshHotLore(stack){
 if(!stack)return stack;const until=hotUntil(stack);
 try{
  if(until<=0)return stack;const left=Math.max(0,until-now());
  if(left<=0){stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore([]);return stack}
  const sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');
  stack.setLore(['§c🔥 煙火氣 '+m+':'+s]);
 }catch{}return stack;
}
function cookedStack(raw,state){
 let stack;
 if(raw?.typeId===SECRET_ID&&!isSecretCooked(raw))stack=cookSecret(raw);
 else{const out=RAW_TO_COOKED[raw.typeId];if(!out)return new ItemStack(MYSTERIOUS_ID,1);stack=new ItemStack(out,1)}
 setHot(stack,state.heatTicks);setSeasonings(stack,state.seasonings??[]);
 try{stack.setDynamicProperty('kaleidoscope_grilling:seasoned',state.seasoned)}catch{}
 return refreshHotLore(stack);
}
function outputFor(raw,state,kind){
 if(kind==='raw')return copyOne(raw);
 if(kind==='dark'||kind==='mysterious'){const out=new ItemStack(kind==='dark'?DARK_ID:MYSTERIOUS_ID,1);if(readIngredients(raw).length)copySkewerProperties(raw,out);return out}
 return cookedStack(raw,state)
}
function extract(block,player,all=false){
 const state=readState(block);if(!canExtract(state))return 0;const c=inv(block);if(!c)return 0;let count=0;
 for(let i=0;i<3;i++){const raw=c.getItem(i);if(!raw)continue;give(player,outputFor(raw,state,outputKind(state)));c.setItem(i,undefined);count++;if(!all)break}
 if(occupied(block)===0)resetBlock(block,state.lit);if(count)try{block.dimension.playSound('random.pop',block.location)}catch{}return count;
}
function customBreak(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;const state=readState(block),kind=breakDisposition(state),c=inv(block);
 if(c)for(let i=0;i<3;i++){const raw=c.getItem(i);if(raw)player.dimension.spawnItem(outputFor(raw,state,kind),{x:block.x+.5,y:block.y+.4,z:block.z+.5})}
 clearContainer(block);clearState(block);block.setType('minecraft:air');
 if(!creative(player))player.dimension.spawnItem(new ItemStack(GRILL_ID,1),{x:block.x+.5,y:block.y+.3,z:block.z+.5});
}
function cookeryOilCount(stack){if(stack?.typeId!==COOKERY_FILLED)return 0;try{const raw=stack.getDynamicProperty(COOKERY_OIL_KEY);return raw===undefined?256:Math.max(0,Math.min(256,Number(raw)|0))}catch{return 256}}
function cookeryOilType(stack){try{const type=String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'canola');return Object.hasOwn(OIL_TYPES,type)?type:'canola'}catch{return 'canola'}}
function heatForOil(type){return OIL_TYPES[type]?.heatTicks??OIL_TYPES.canola.heatTicks}
function consumeCookeryOil(player,needed){
 const stack=heldMain(player);if(stack?.typeId!==COOKERY_FILLED)return {ok:false,reason:'not_pot'};
 const count=cookeryOilCount(stack);if(count<needed)return {ok:false,reason:'insufficient',count};
 const type=cookeryOilType(stack);if(creative(player))return {ok:true,heat:heatForOil(type),remaining:count};
 const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1);
 if(remaining>0){try{next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type!=='canola')next.setDynamicProperty('kaleidoscope_grilling:oil_type',type);next.setLore(['§7Oil: '+remaining+'/256'])}catch{}}
 setMain(player,next);return {ok:true,heat:heatForOil(type),remaining};
}
function consumeSeasoningBottle(player,needed){
 const stack=heldMain(player);if(stack?.typeId!==SEASONING_ID)return {ok:false,reason:'not_seasoning'};
 const uses=getUses(stack),remaining=16-uses;if(remaining<needed)return {ok:false,reason:'insufficient',remaining};
 const ingredients=readSeasonings(stack);if(creative(player))return {ok:true,ingredients,uses};
 const next=uses+needed;if(next>=16)setMain(player,new ItemStack(EMPTY_SEASONING_ID,1));
 else{setUses(stack,next);try{stack.setLore(['§7Uses: '+(16-next)+'/16'])}catch{}setMain(player,stack)}
 return {ok:true,ingredients,uses:next};
}
function handleGrill(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;register(block);let state=readState(block);const held=heldMain(player),id=held?.typeId,n=occupied(block);
 if(id==='minecraft:flint_and_steel'){if(!state.lit){state=light(state,true);writeState(block,state);try{block.dimension.playSound('fire.ignite',block.location)}catch{}message(player,'§6烤爐已點火')}return}
 if(id===COOKERY_FILLED){
  if(state.phase!==0||n<1||!state.lit){message(player,state.lit?'§7現在不能刷油':'§c烤爐尚未點火');return}
  const oil=consumeCookeryOil(player,n);if(!oil.ok){message(player,oil.reason==='insufficient'?'§c油量不足：需要 '+n+'，目前 '+oil.count:'§7需要森羅物語裝油的油壺');return}
  const result=brush(state,n,oil.heat);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.main',{blendOutTime:.12})}catch{}message(player,'§e刷油完成，消耗 '+(creative(player)?0:n)+' 點油')}return;
 }
 if(id&&Object.hasOwn(OIL_TOOLS,id)){const result=brush(state,n,OIL_TOOLS[id]);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.brush.main',{blendOutTime:.12})}catch{}message(player,'§8相容刷具：已刷油；正式流程請使用 Cookery 油壺')}return}
 if(id===SEASONING_ID){
  if(state.phase!==2||state.seasoned||n<1){message(player,'§7現在不能撒料');return}
  const bottle=consumeSeasoningBottle(player,n);if(!bottle.ok){message(player,bottle.reason==='insufficient'?'§c調料不足：爐上 '+n+' 串需要 '+n+' 次，剩 '+bottle.remaining+' 次':'§7需要完成的調料瓶');return}
  const result=season(state,n,bottle.ingredients);if(result.ok){writeState(block,result.state);try{player.playAnimation('animation.kg_imm.player.season.main',{blendOutTime:.12})}catch{}message(player,'§a調味完成，消耗 '+(creative(player)?0:n)+' 次')}return;
 }
 if(id&&(Object.hasOwn(RAW_TO_COOKED,id)||(id===SECRET_ID&&!isSecretCooked(held)))){if(!state.lit){message(player,'§c需要先點火');return}if(!canInsert(state,n)){message(player,'§7烤爐現在不能再放入生串');return}const c=inv(block),slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;c.setItem(slot,copyOne(held));decrementMain(player);message(player,'§a已放入烤串 '+(slot+1)+'/3');return}
 if(id){message(player,'§7這個物品不能用在目前的烤爐階段');return}
 if(state.phase===1){const r=flip(state);if(r.ok){writeState(block,r.state);try{player.playAnimation('animation.kg_imm.player.reach.main',{blendOutTime:.1});block.dimension.playSound('kg_imm.grill_flip',block.location)}catch{}message(player,'§e翻面 '+r.state.flips+'/4')}else message(player,'§7翻面冷卻中');return}
 if(state.phase===0&&n>0){message(player,'§e還需要刷油');return}if(state.phase===2&&!state.seasoned){message(player,'§e還需要撒料');return}
 if(canExtract(state)){const got=extract(block,player,player.isSneaking);if(got)message(player,'§a取出 '+got+' 串')}
}
function readBottleStack(block){
 try{
  const raw=world.getDynamicProperty(seasoningBlockKey(block));if(raw===undefined)return [];
  const v=JSON.parse(raw);if(!Array.isArray(v))return [];
  if(v.length&&typeof v[0]==='string'){const list=v.filter(x=>typeof x==='string').slice(0,8);return [{kind:hasSeasoningBase(list)?'pending':'empty',ingredients:list,uses:0,variant:0}]}
  return v.slice(0,4).map(x=>({kind:['empty','pending','special'].includes(x?.kind)?x.kind:'empty',ingredients:Array.isArray(x?.ingredients)?x.ingredients.filter(y=>typeof y==='string').slice(0,8):[],uses:Math.max(0,Math.min(16,Number(x?.uses)||0)),variant:Math.max(0,Math.min(7,Number(x?.variant)||0))}));
 }catch{return []}
}
function writeBottleStack(block,stack){world.setDynamicProperty(seasoningBlockKey(block),stack.length?JSON.stringify(stack.slice(0,4)):undefined)}
function bottleDataFromItem(stack){
 const kind=stack?.typeId===SEASONING_ID?'special':stack?.typeId===PENDING_SEASONING?'pending':'empty';
 return {kind,ingredients:readSeasonings(stack),uses:kind==='special'?getUses(stack):0,variant:kind==='special'?Math.max(0,Math.min(7,Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)??0)|0)):0};
}
function bottleItem(data){
 const id=data.kind==='special'?SEASONING_ID:data.kind==='pending'?PENDING_SEASONING:EMPTY_SEASONING_ID,stack=new ItemStack(id,1);setSeasonings(stack,data.ingredients??[]);
 if(data.kind==='special'){setUses(stack,data.uses??0);try{stack.setDynamicProperty(SEASON_VARIANT_KEY,data.variant??0);stack.setLore(['§7Uses: '+(16-(data.uses??0))+'/16','§7Ingredients: '+(data.ingredients?.length??0)+'/8'])}catch{}}
 else try{if(data.ingredients?.length)stack.setLore(['§7Ingredients: '+data.ingredients.length+'/8',data.kind==='pending'?'§eReady to shake':'§7Missing base seasoning'])}catch{}
 return stack;
}
function setBottleVisual(block,count){
 const target=count>0?'kaleidoscope_grilling:seasoning_bottle_'+Math.max(1,Math.min(4,count)):'minecraft:air';
 if(block.typeId!==target)block.setType(target);
}
function pushBottle(block,player,held){
 const stack=readBottleStack(block);if(stack.length>=4){message(player,'§c最多只能堆4瓶');return false}
 stack.push(bottleDataFromItem(held));if(!decrementMain(player))return false;writeBottleStack(block,stack);setBottleVisual(block,stack.length);message(player,'§a調料瓶堆疊 '+stack.length+'/4');return true;
}
function handleSeasoningBlock(block,player){
 let stack=readBottleStack(block);if(!stack.length)stack=[{kind:'empty',ingredients:[],uses:0,variant:0}];
 const held=heldMain(player),id=held?.typeId;
 if(id===EMPTY_SEASONING_ID||id===PENDING_SEASONING||id===SEASONING_ID){pushBottle(block,player,held);return}
 const top=stack[stack.length-1];
 if(id&&Object.hasOwn(SEASONING_KINDS,id)){
  if(top.kind==='special'){message(player,'§7最上層是完成調料，不能再加料');return}
  if(top.ingredients.length>=8){message(player,'§c最上層調料瓶已滿 8/8');return}
  top.ingredients.push(id);top.kind=hasSeasoningBase(top.ingredients)?'pending':'empty';if(!decrementMain(player))return;writeBottleStack(block,stack);
  try{block.dimension.spawnParticle('minecraft:endrod',{x:block.x+.5,y:block.y+.7,z:block.z+.5})}catch{}
  message(player,hasSeasoningBase(top.ingredients)?'§a已加入 '+top.ingredients.length+'/8；基礎三料齊全':'§e已加入 '+top.ingredients.length+'/8');return;
 }
 if(!id){
  const out=stack.pop();setMain(player,bottleItem(out));writeBottleStack(block,stack);setBottleVisual(block,stack.length);message(player,'§a取回最上層調料瓶，剩 '+stack.length+'/4');return;
 }
 message(player,'§7這不是可加入的調料或調料瓶');
}
function placeSeasoningState(block,player){
 const cached=SEASON_PLACE_CACHE.get(player.id);SEASON_PLACE_CACHE.delete(player.id);
 const data=cached&&system.currentTick-cached.tick<=8?cached.data:{kind:'empty',ingredients:[],uses:0,variant:0};writeBottleStack(block,[data]);setBottleVisual(block,1);
}
function readFx(entity){try{const raw=entity.getDynamicProperty(FX_KEY);if(typeof raw!=='string')return {};const v=JSON.parse(raw);return v&&typeof v==='object'?v:{}}catch{return {}}}
function writeFx(entity,fx){try{const clean={};for(const [k,v] of Object.entries(fx))if(v&&Number(v.until)>now())clean[k]={until:Number(v.until),amp:Number(v.amp)||0};entity.setDynamicProperty(FX_KEY,Object.keys(clean).length?JSON.stringify(clean):undefined)}catch{}}
function fxGet(entity,name){const v=readFx(entity)[name];return v&&Number(v.until)>now()?v:null}
function fxSet(entity,name,ticks,amp=0){const fx=readFx(entity);fx[name]={until:now()+Math.max(1,ticks|0),amp:amp|0};writeFx(entity,fx)}
function fxClear(entity,name){const fx=readFx(entity);delete fx[name];writeFx(entity,fx)}
function fxReduce(entity,name,ticks){const fx=readFx(entity),v=fx[name];if(!v)return;v.until-=ticks;if(v.until<=now())delete fx[name];writeFx(entity,fx)}
function fxSnapshot(entity){return JSON.parse(JSON.stringify(readFx(entity)))}
function nativeSnapshot(entity){const out={};try{for(const e of entity.getEffects())out[e.typeId]={duration:e.duration,amplifier:e.amplifier}}catch{}return out}
function doubleNewNative(player,before){try{for(const e of player.getEffects()){const old=before[e.typeId]?.duration??0;if(e.duration<=old)continue;const duration=old+(e.duration-old)*2;player.removeEffect(e.typeId);player.addEffect(e.typeId,Math.max(1,duration),{amplifier:e.amplifier,showParticles:true})}}catch{}}
function doubleNewFx(player,before){const current=readFx(player),t=now();for(const [name,v] of Object.entries(current)){if(name==='invincible')continue;const old=before[name]?.until??t;if(v.until<=old)continue;v.until=old>t?old+(v.until-old)*2:t+(v.until-t)*2}writeFx(player,current)}
function applyFixedEffect(player,id){
 const e=COOKED_EFFECTS[id];if(!e||!e.effect)return;const ticks=Math.max(1,e.seconds*20);
 if(e.effect.startsWith('minecraft:')){try{player.addEffect(e.effect.split(':')[1],ticks,{showParticles:true})}catch{}return}
 if(e.effect==='kaleidoscope_grilling:invincible'){fxSet(player,'invincible',ticks);return}
 if(e.effect.startsWith('kaleidoscope_cookery:'))fxSet(player,e.effect.split(':')[1],ticks);
}
function counts(list){const out={};for(const id of list){const kind=SEASONING_KINDS[id];if(kind)out[kind]=(out[kind]??0)+1}return out}
function dragonPool(entity){try{return Math.max(0,Math.min(2,Number(entity.getDynamicProperty(DRAGON_POOL_KEY)??0)))}catch{return 0}}
function setDragonPool(entity,value){try{entity.setDynamicProperty(DRAGON_POOL_KEY,value>0?Math.max(0,Math.min(2,value)):undefined)}catch{}}
function applyDragonBlood(player,ticks,amp){
 const old=fxGet(player,'dragon_blood'),oldNative=old?(old.amp>0?8:4):0,newNative=amp>0?8:4;
 fxSet(player,'dragon_blood',ticks,amp);
 if(!old)setDragonPool(player,2);
 try{player.addEffect('health_boost',Math.max(25,ticks),{amplifier:amp>0?1:0,showParticles:false})}catch{}
 const gain=Math.max(0,newNative-oldNative);
 if(gain>0)system.run(()=>{try{const hp=player.getComponent('minecraft:health');if(hp)hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+gain))}catch{}});
}

function applySeasoning(player,list){
 const c=counts(list);let duration=3600;if((c.duration??0)>=4)duration*=4;else if((c.duration??0)>0)duration*=2;
 if((c.speed??0)>0)try{player.addEffect('speed',duration,{amplifier:c.speed>=4?1:0,showParticles:true})}catch{}
 if((c.strength??0)>0)try{player.addEffect('strength',duration,{amplifier:c.strength>=4?1:0,showParticles:true})}catch{}
 if((c.numbness??0)>=4)fxSet(player,'numb',900*((c.duration??0)>=4?4:(c.duration??0)>0?2:1));
 if((c.totem??0)>0&&!fxGet(player,'heavy_metal_poisoning'))fxSet(player,'heavy_metal',duration,c.totem>=4?1:0);
 if((c.vitality??0)>0)applyDragonBlood(player,duration,c.vitality>=4?1:0);
}
function dangerousPreservation(player,itemId){if(!DANGEROUS_FOODS.has(itemId)||!fxGet(player,'preservation'))return;for(const id of ['hunger','poison','nausea'])try{player.removeEffect(id)}catch{}}
function applyOrdinary(player){
 const challenged=!!fxGet(player,'invincible');if(challenged)fxClear(player,'invincible');
 if(challenged&&Math.random()<.5){try{player.dimension.playSound('random.shield_block',player.location);player.dimension.spawnParticle('minecraft:electric_spark_particle',{x:player.location.x,y:player.location.y+1,z:player.location.z})}catch{}message(player,'§6普通串被無敵擋下');return}
 system.run(()=>{try{player.kill()}catch{try{player.applyDamage(100000,{cause:'override'})}catch{}}});
}
function afterCommitted(player,id,meta,active,fullNative){
 applyFixedEffect(player,id);
 if(meta.hot){doubleNewNative(player,active.nativeBefore);doubleNewFx(player,active.fxBefore)}
 if(meta.hot&&fullNative&&active.saturationBefore!==undefined){const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(h&&sat){const gained=Math.max(0,sat.currentValue-active.saturationBefore);sat.setCurrentValue(Math.min(h.currentValue,active.saturationBefore+gained*1.25))}}
 if(meta.hot)applySeasoning(player,meta.seasonings);
 if(id==='kaleidoscope_grilling:grilled_golden_skewer')try{player.dimension.playSound('beacon.power',player.location)}catch{}
 if(id==='kaleidoscope_grilling:ordinary_skewer')applyOrdinary(player);
}
function stackMeta(stack){return {hot:isHot(stack),seasonings:readSeasonings(stack),hotUntil:hotUntil(stack)}}
function foodDataFor(stack){if(stack?.typeId===SECRET_ID)return secretFoodStats(stack);return FOOD_DATA[stack?.typeId]}
function settleSecretNative(player,active){
 if(active?.id!==SECRET_ID||!active.foodData)return;
 const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!h||!sat)return;
 const d=active.foodData,bh=Number(active.hungerBefore),bs=Number(active.saturationBefore);
 if(Number.isFinite(bh)){const hunger=Math.min(h.effectiveMax,bh+d.nutrition);h.setCurrentValue(hunger);if(Number.isFinite(bs))sat.setCurrentValue(Math.min(hunger,bs+d.nutrition*d.saturation*2))}
}
function hungerSettle(player,id,active){
 const d=active?.foodData??FOOD_DATA[id];if(!d)return false;const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!h||!sat)return false;
 const hunger=Math.min(h.effectiveMax,h.currentValue+d.nutrition);h.setCurrentValue(hunger);const baseGain=d.nutrition*d.saturation*2*(active.meta.hot?1.25:1);sat.setCurrentValue(Math.min(hunger,sat.currentValue+baseGain));
 let stack=active.hand==='off'?heldOff(player):heldMain(player);if(!stack||stack.typeId!==id)return false;if(stack.amount<=1)setHand(player,active.hand,undefined);else{stack.amount-=1;setHand(player,active.hand,stack)}
 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(player,id,active.meta,active,false);return true;
}
function resolvedProfile(profile){return profile==='THREE_RANDOM'?(Math.random()<.5?'THREE':'THREE_ALT'):profile}
function profileDuration(profile){return profile==='THREE'?100:90}
function completePending(player,stack){
 const list=readSeasonings(stack);if(!hasSeasoningBase(list)){message(player,'§c缺少基礎三料，不能完成調料');return}
 const hand=handFor(player,PENDING_SEASONING)?.name??'main',out=new ItemStack(SEASONING_ID,1);setSeasonings(out,list);setUses(out,0);
 try{out.setDynamicProperty(SEASON_VARIANT_KEY,Math.floor(Math.random()*8));out.setLore(['§7Uses: 16/16','§7Ingredients: '+list.length+'/8'])}catch{};setHand(player,hand,out);message(player,'§a調料搖勻完成');
}
function canThreadHeld(player,item){
 if(player.isSneaking)return canDisassemble(heldOff(player));
 const off=heldOff(player);if(!isThreadTarget(off)||!item)return false;
 let edible=false;try{edible=!!item.getComponent('minecraft:food')}catch{}
 const ids=off.typeId==='minecraft:stick'?[]:readIngredients(off);
 return canAppend(ids,item.typeId,edible);
}
function putBack(player,stack){if(stack?.amount>0)give(player,stack)}
function threadHeld(player){
 if(THREAD_LAST.get(player.id)===system.currentTick)return false;
 const off=heldOff(player),main=heldMain(player);if(!off)return false;
 if(player.isSneaking&&canDisassemble(off)){
  const returned=disassemblyItems(off);if(!returned.length)return false;
  const remain=off.clone();remain.amount-=1;setOff(player,remain.amount>0?remain:undefined);
  for(const item of returned)putBack(player,item);
  THREAD_LAST.set(player.id,system.currentTick);try{player.playSound('random.pop',{volume:.7,pitch:1})}catch{};message(player,'§e已拆解烤串並返還食材與木棍');return true;
 }
 if(player.isSneaking||!main||!isThreadTarget(off))return false;
 const result=createThreaded(off,main,player.name,player.id);if(!result)return false;
 if(!creative(player)){
  if(!decrementMain(player))return false;
  if(off.typeId==='minecraft:stick'&&off.amount>1){const rem=off.clone();rem.amount-=1;putBack(player,rem)}
 }else if(off.typeId==='minecraft:stick')putBack(player,off.clone());
 setOff(player,result.stack);THREAD_LAST.set(player.id,system.currentTick);
 try{player.playSound('random.pop',{volume:.7,pitch:1.15})}catch{}
 message(player,result.fixed?'§a固定串配方完成':result.completed?'§d完成秘制烤串':'§e已穿入食材 '+result.ingredients.length+'/3');
 return true;
}
try{world.beforeEvents.itemUse.subscribe(e=>{
 const p=e.source;if(!p||!canThreadHeld(p,e.itemStack))return;e.cancel=true;system.run(()=>threadHeld(p));
})}catch{}
world.afterEvents.itemStartUse.subscribe(e=>{
 const id=e.itemStack?.typeId;
 if(id===PENDING_SEASONING){const hand=handFor(e.source,id)?.name??'main';try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 const foodData=foodDataFor(e.itemStack);if(!foodData)return;
 const requested=id===SECRET_ID?'THREE_RANDOM':(PROFILE_BY_ITEM[id]??'THREE'),hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(requested),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation'),hunger=e.source.getComponent('minecraft:player.hunger');
 const a={id,start:system.currentTick,requested,profile,hand,meta,foodData,biteTimes:BITE_TIMES[profile]??BITE_TIMES.THREE,nextBite:0,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},hungerBefore:hunger?.currentValue,saturationBefore:sat?.currentValue};
 ACTIVE_EATS.set(e.source.id,a);
 try{e.source.playAnimation('animation.kg_imm.player.eat_'+profile.toLowerCase()+'.'+hand,{blendOutTime:.12});e.source.playSound('kg_imm.'+soundFor(profile))}catch{}
});
world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 dangerousPreservation(e.source,id);const current=ACTIVE_EATS.get(e.source.id),foodData=foodDataFor(e.itemStack)??current?.foodData;if(!foodData)return;
 const a=current??{id,profile:id===SECRET_ID?'THREE':(PROFILE_BY_ITEM[id]??'THREE'),meta:stackMeta(e.itemStack),foodData,nativeBefore:{},fxBefore:{},hungerBefore:undefined,saturationBefore:undefined};stopEatSound(e.source,a.profile);SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(id===SECRET_ID)settleSecretNative(e.source,a);
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(e.source,id,a.meta,a,true);
});
world.afterEvents.itemStopUse.subscribe(e=>{const a=ACTIVE_EATS.get(e.source.id);if(!a)return;ACTIVE_EATS.delete(e.source.id);stopEatSound(e.source,a.profile);if(SETTLED.get(e.source.id)===system.currentTick)return;const used=system.currentTick-a.start;if(used>=25&&used<profileDuration(a.profile)){if(hungerSettle(e.source,a.id,a))message(e.source,'§a在1.25秒檢查點完成進食')}try{e.source.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}});
world.beforeEvents.entityHurt.subscribe(e=>{
 const target=e.hurtEntity,cause=e.damageSource?.cause;
 if(fxGet(target,'invincible')&&cause!=='selfDestruct'&&cause!=='override'){e.cancel=true;system.run(()=>{try{target.dimension.playSound('random.shield_block',target.location)}catch{}});return}
 if(e.damageSource?.damagingProjectile&&fxGet(target,'projectile_dodge')){e.cancel=true;system.run(()=>{fxReduce(target,'projectile_dodge',200);const base=target.location;for(let i=0;i<16;i++){const to={x:base.x+(Math.random()-.5)*3,y:base.y+(Math.random()-.5)*3,z:base.z+(Math.random()-.5)*3};try{if(target.tryTeleport(to,{checkForBlocks:true})){target.dimension.playSound('mob.endermen.portal',target.location);break}}catch{}}});return}
 const replay=DRAGON_REPLAY.delete(target.id);
 if(!replay){
  const db=fxGet(target,'dragon_blood'),pool=dragonPool(target);
  if(db&&pool>0&&e.damage>0){
   const absorb=Math.min(pool,e.damage),remain=e.damage-absorb;setDragonPool(target,pool-absorb);e.cancel=true;
   if(remain>0)system.run(()=>{try{DRAGON_REPLAY.add(target.id);const opt={cause:e.damageSource?.cause??'entityAttack'};if(e.damageSource?.damagingEntity)opt.damagingEntity=e.damageSource.damagingEntity;target.applyDamage(remain,opt)}catch{DRAGON_REPLAY.delete(target.id)}});
   return;
  }
 }
 const hm=fxGet(target,'heavy_metal'),hp=target.getComponent?.('minecraft:health');if(hm&&!fxGet(target,'heavy_metal_poisoning')&&hp&&e.damage>=hp.currentValue){e.cancel=true;system.run(()=>{fxClear(target,'heavy_metal');fxSet(target,'heavy_metal_poisoning',12000);try{hp.setCurrentValue(1);target.dimension.playSound('random.totem',target.location)}catch{}})}
});
world.afterEvents.entityHitEntity.subscribe(e=>{if(fxGet(e.damagingEntity,'hinder'))try{e.hitEntity.addEffect('slowness',100,{amplifier:1,showParticles:true})}catch{}});
world.beforeEvents.playerPlaceBlock.subscribe(e=>{try{if(e.permutationToPlace?.type?.id!==SEASONING_BLOCK)return;const held=heldMain(e.player);if(!held||![EMPTY_SEASONING_ID,PENDING_SEASONING,SEASONING_ID].includes(held.typeId))return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,data:bottleDataFromItem(held)})}catch{}});
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(canThreadHeld(e.player,e.itemStack)){e.cancel=true;const p=e.player;system.run(()=>threadHeld(p));return}
 if(e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;const r=compactSkewerContainer(c,false);message(p,r.changed?'§b已整理串類：熱度差≤5分鐘的熱串按數量加權合併':'§7沒有可整理的串類')});return;
 }
 if(e.block.typeId!==GRILL_ID&&!isSeasoningBlock(e.block.typeId))return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)});
});
world.afterEvents.playerPlaceBlock.subscribe(e=>{if(e.block.typeId===GRILL_ID){register(e.block);resetBlock(e.block,false)}else if(isSeasoningBlock(e.block.typeId))placeSeasoningState(e.block,e.player)});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.block.typeId===GRILL_ID){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>customBreak(dim.getBlock(loc),p));return}
 if(isSeasoningBlock(e.block.typeId)){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const b=dim.getBlock(loc);if(!b||!isSeasoningBlock(b.typeId))return;const bottles=readBottleStack(b);writeBottleStack(b,[]);b.setType('minecraft:air');if(!creative(p))for(const data of bottles)b.dimension.spawnItem(bottleItem(data),{x:loc.x+.5,y:loc.y+.4,z:loc.z+.5})})}
});
function nearHeat(player){
 const p=player.location,d=player.dimension;for(let x=-2;x<=2;x++)for(let y=-1;y<=1;y++)for(let z=-2;z<=2;z++){try{const b=d.getBlock({x:Math.floor(p.x)+x,y:Math.floor(p.y)+y,z:Math.floor(p.z)+z});if(!b)continue;if(HEAT_BLOCKS.has(b.typeId))return true;if(b.typeId===GRILL_ID&&readState(b).lit)return true;if(['minecraft:furnace','minecraft:smoker','minecraft:blast_furnace'].includes(b.typeId)&&b.permutation.getState('lit')===true)return true}catch{}}return false;
}
function fleeCreepers(player){
 try{for(const e of player.dimension.getEntities({type:'minecraft:creeper',location:player.location,maxDistance:6})){const dx=e.location.x-player.location.x,dz=e.location.z-player.location.z,len=Math.max(.001,Math.hypot(dx,dz));e.applyKnockback({x:dx/len*.12,z:dz/len*.12},.02)}}catch{}
}
function repelPhantoms(player){
 try{for(const e of player.dimension.getEntities({type:'minecraft:phantom',location:player.location,maxDistance:18})){const dx=e.location.x-player.location.x,dy=e.location.y-player.location.y,dz=e.location.z-player.location.z;if(Math.abs(dx)>8||Math.abs(dz)>8||Math.abs(dy)>16)continue;const len=Math.max(.001,Math.hypot(dx,dz));e.applyKnockback({x:dx/len*.16,z:dz/len*.16},.06)}}catch{}
}
function tundraFactor(id){if(id==='minecraft:blue_ice')return 1.1055;if(['minecraft:ice','minecraft:packed_ice','minecraft:frosted_ice'].includes(id))return 1.11;return 1.3}
system.runInterval(()=>{
 const rows=readRegistry(),keep=[];
 for(const row of rows){try{const block=world.getDimension(row.d).getBlock({x:row.x,y:row.y,z:row.z});if(!block||block.typeId!==GRILL_ID)continue;keep.push(row);let state=readState(block),before=state.phase;const result=tickState(state,occupied(block),1);state=result.state;if(result.events.some(x=>x.kind==='burn_to_charcoal')){const count=1+Math.floor(Math.random()*2);clearContainer(block);block.dimension.spawnItem(new ItemStack('minecraft:charcoal',count),{x:block.x+.5,y:block.y+.4,z:block.z+.5});writeState(block,state);continue}if(before!==state.phase)try{block.dimension.playSound('fire.fire',block.location)}catch{};writeState(block,state);if(state.lit&&system.currentTick%4===0){const p={x:block.x+.5+(Math.random()-.5)*.45,y:block.y+.35,z:block.z+.5+(Math.random()-.5)*.45};if(Math.random()<.35)block.dimension.spawnParticle('minecraft:basic_smoke_particle',p);if(Math.random()<.12)block.dimension.spawnParticle('minecraft:basic_flame_particle',p)}}catch{}}
 if(keep.length!==rows.length)saveRegistry(keep);
 for(const p of world.getAllPlayers()){try{
  const active=ACTIVE_EATS.get(p.id);
  if(active){advanceBites(p,active);if(active.requested==='THREE_RANDOM'&&active.profile==='THREE_ALT'&&system.currentTick-active.start>=90){ACTIVE_EATS.delete(p.id);SETTLED.set(p.id,system.currentTick);stopEatSound(p,active.profile);if(hungerSettle(p,active.id,active))try{p.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}}}
  writeFx(p,readFx(p));const hunger=p.getComponent('minecraft:player.hunger'),sat=p.getComponent('minecraft:player.saturation');
  if(fxGet(p,'vigor')&&hunger&&sat){const prev=VIGOR_LAST.get(p.id);if(p.isSprinting&&prev){if(hunger.currentValue<prev.hunger)hunger.setCurrentValue(prev.hunger);if(sat.currentValue<prev.sat)sat.setCurrentValue(prev.sat)}VIGOR_LAST.set(p.id,{hunger:hunger.currentValue,sat:sat.currentValue})}else VIGOR_LAST.delete(p.id);
  const sneak=!!p.isSneaking,was=SNEAK_LAST.get(p.id)??false;if(sneak&&!was&&fxGet(p,'flatulence')){p.applyImpulse({x:0,y:.75,z:0});try{p.dimension.spawnParticle('minecraft:basic_smoke_particle',{x:p.location.x,y:p.location.y+.25,z:p.location.z});p.dimension.playSound('random.fizz',p.location)}catch{}}SNEAK_LAST.set(p.id,sneak);
  if(system.currentTick%5===0){if(fxGet(p,'mustard'))fleeCreepers(p);if(fxGet(p,'sulfur'))repelPhantoms(p)}
  if(fxGet(p,'tundra_strider')){try{const b=p.getBlockStandingOn();if(b&&TUNDRA_BLOCKS.has(b.typeId)){const v=p.getVelocity(),factor=tundraFactor(b.typeId);p.applyImpulse({x:v.x*(factor-1),y:0,z:v.z*(factor-1)});if(b.typeId==='minecraft:powder_snow'&&v.y<.02)p.applyImpulse({x:0,y:Math.min(.16,Math.max(.04,-v.y+.04)),z:0})}}catch{}}
  if(system.currentTick%20===0&&fxGet(p,'warmth')){const hp=p.getComponent('minecraft:health');if(hp&&hp.currentValue<hp.effectiveMax){if(nearHeat(p))hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+1));else if(p.dimension.id==='minecraft:nether'&&Math.random()<.25)hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+.5))}}
  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db){try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{};if(dragonPool(p)<=0&&p.getDynamicProperty(DRAGON_POOL_KEY)===undefined)setDragonPool(p,2)}else setDragonPool(p,0)}
  const numb=fxGet(p,'numb');if(numb&&!ACTIVE_EATS.has(p.id)){if(system.currentTick%12===0)try{p.playAnimation('animation.kg_a22.player.numb',{blendOutTime:.08})}catch{};NUMB_VISUAL.add(p.id)}else if(!numb&&NUMB_VISUAL.delete(p.id)){try{p.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}}
  if(system.currentTick%20===0){const m=heldMain(p),o=heldOff(p);if(m&&hotUntil(m)>0){refreshHotLore(m);setMain(p,m)}if(o&&hotUntil(o)>0){refreshHotLore(o);setOff(p,o)}}
 }catch{}}
},1);
