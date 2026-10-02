import {planDragonDamage,dragonHealthGain} from './dragon_health_core.js';
import {configureSecretVisuals} from './station_contents_visual_runtime.js';
import {foodFacts} from './food_snapshot_core.js';
import {updateGrillAudio,removeGrillAudio,blockSound,useSound,stopSoundHandle,seasoningFinished} from './immersion_audio_runtime.js';
import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {readNativeBottles,isNativeBottleItem} from './seasoning_native_storage.js';
import {slotWrite} from './rack_transfer_plan.js';
import {acknowledgedDrop,commitStationTransfer} from './grill_transfer.js';
import './dragon_powder_runtime.js';
import './a288_parity_runtime.js';
import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,setItemLore} from './itemData.js';
import {hasSolidTop} from './blockSupport.js';
import {stationContainer,retireEmptyStationContainer,quarantineStation,inspectStationStorage,storageKey as stationStorageKey} from './family_station_storage.js';
import {rolledIngredientEffects} from './a285_ingredient_effects.js';
import {resolveSecretSmokedId} from './secret_compat_core.js';
import {emitSecretIngredientConsumed} from './secret_compat_runtime.js';
import {
 skewerIngredientDecision,customSkewerCookedId,isCompatRawSkewer
} from './skewer_compat_core.js';
import './skewer_compat_runtime.js';
import {EquipmentSlot,GameMode,EnchantmentType} from '@minecraft/server';
import {captureEatingIdentity,eatingStillCurrent,eatingEventMatches,commitEating} from './a285_eating_transaction.js';
import {completedUseStillCurrent} from './a2810_use_transaction.js';
import {interactionFeedback,interactionFailure,javaInteractionFeedback} from './a283_interaction_feedback.js';
import {showJavaEatingHud} from './java_eating_hud_runtime.js';
import './a2770_placed_visual_runtime.js';
import './guide/main.js';
import {world,system,ItemStack} from '@minecraft/server';
import {RAW_TO_COOKED,FOOD_DATA,PROFILE_BY_ITEM,COOKED_EFFECTS,RAW_NAUSEA,OIL_TOOLS,GRILL_ID,SEASONING_ID,EMPTY_SEASONING_ID,MYSTERIOUS_ID,DARK_ID} from './data.js';
import {initialState,normalizeState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';
import {grillStateKey as stateKey,readGrillState as readState,occupiedGrillSlots as occupied} from './a2740_grill_state_adapter.js';
import {mergeIntoContainer,compactSkewerContainer,compactMatchingHotFood,isFoodStack} from './a23_hot_runtime.js';
import './a23_oil_world.js';
import {UNFINISHED_ID,SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY,SECRET_COOKED_INGREDIENTS_KEY,SECRET_CREATOR_KEY,FLUID_CAPACITY,appendOutcome,secretFood,isDisassemblableRaw,canAppendConfigured,isConfiguredIngredient} from './a24_skewering_core.js';
import {PLATE_ID,plateHighestNutritionIndex} from './a25_plate_recipe_core.js';
import {a25PlateRows,a25PlateItem,a25RestoreStack} from './a25_plate_recipe_runtime.js';
import './a26_oil_machine_runtime.js';
import './a2727_cookery_host_recipes_runtime.js';
import {COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryOilPotConsumption} from './a2734_cookery_oil_pot_adapter.js';
import {ensureOilHandPublished} from './oil_api_client.js';
import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,findHandEntry as handFor,setHand,isCreative as creative} from './a2735_player_io.js';
import {
 SEASONING_CAPACITY,SEASONING_MAX_BOTTLES,SEASONING_MAX_USES,SEASONING_VARIANT_MAX,
 PENDING_SEASONING_ID as PENDING_SEASONING,SEASONING_PLACE_BLOCK_ID as SEASONING_BLOCK,
 SEASONING_USES_KEY as SEASON_USES_KEY,
 SEASONING_VARIANT_KEY as SEASON_VARIANT_KEY,SEASONING_KINDS,
 hasSeasoningBase,isSeasoningBlockId as isSeasoningBlock
} from './a2743_seasoning_contract_core.js';
import {
 readPlacedSeasoningStack as readBottleStack,writePlacedSeasoningStack as writeBottleStack
} from './a2743_seasoning_block_adapter.js';
import {
 readFoodSeasonings as readSeasonings,setFoodSeasonings as setSeasonings,
 setHotFood as setHot,hotUntil,isHotFood as isHot,refreshHotLore
} from './a2750_food_state_adapter.js';
import {WOK_FOOD_IDS} from './a2750_wok_food_core.js';
import {STOCKPOT_FOOD_IDS} from './a2752_stockpot_food_core.js';
import './a2736_typed_oil_pot_block_runtime.js';
import './a2737_offhand_oil_fill_runtime.js';
import './a2739_crosshair_hud_runtime.js';
import './a2739_oil_pot_hud_provider.js';
import './a2740_grill_hud_provider.js';
import './a2741_oil_press_hud_provider.js';
import './a2742_big_vat_hud_provider.js';
import './a2743_seasoning_hud_provider.js';
import './a2744_skewer_plate_hud_provider.js';
import './a2746_advanced_rack_runtime.js';
import './a2745_skewer_recipe_hud_provider.js';
import './a271_sweet_potato_runtime.js';
import {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';
import './a2710_chicken_acquisition_runtime.js';
import './a2712_remaining_knife_drops_runtime.js';
import './a2714_houttuynia_crop_runtime.js';
import './a2731_farmland_crop_host_runtime.js';
import './a2732_standalone_food_effect_runtime.js';
import './a2747_wedding_candy_runtime.js';
import './a2748_pepper_tree_runtime.js';
import './a2759_pepper_worldgen_fruiting_runtime.js';
import './a2750_cookery_cuisine_runtime.js';
import {awardLookingThePart,awardGleamingWithOil,awardSeasoningMilestones,awardEatItHot} from './a2756_advancement_event_runtime.js';
import {awardSeasoningFinishedChallenges,awardMentalPreparationFailed,awardMetalToleranceFailed,awardOrdinaryChallenge,ordinaryChallengeOutcome} from './a2758_advancement_challenge_runtime.js';
import './a2722_cold_houttuynia_runtime.js';
import {isExtinguishTool,isInitialBlockPress,nextDurability} from './a275_grill_input_core.js';
import {primitiveStackProps,captureInteractionIntent,interactionIntentStillCurrent} from './a2762_interaction_intent_adapter.js';
import {commitSteps,commitTwoParty,chooseExtractDelivery} from './a277_grill_transaction_core.js';
import {captureWritableHand} from './a2735_player_io.js';
import {captureTwoHandIntent,twoHandIntentStillCurrent} from './a2762_interaction_intent_adapter.js';
import {seasoningBlockKey} from './a2743_seasoning_block_adapter.js';
import {markPlacedVisualDirty} from './a2770_placed_visual_queue.js';
import {tickGrillDisplay} from './grill_visual_runtime.js';
import {isSpecialSeasoningId,specialSeasoningVisualId} from './a2766_special_seasoning_visual_core.js';
import {retargetSpecialSeasoningStack,specialSeasoningVariant} from './a2766_special_seasoning_visual_runtime.js';

const GRILL_LEGS_ID='kaleidoscope_grilling:grill_legs';
const ACTIVE_EATS=new Map(),CUISINE_EATS=new Map(),PLATE_EATS=new Map(),PENDING_USES=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),THREAD_LAST=new Map();
const CUISINE_FOOD_SET=new Set([...WOK_FOOD_IDS,...STOCKPOT_FOOD_IDS]);
const FX_KEY='kaleidoscope_grilling:a21_fx';
const HEAT_BLOCKS=new Set(['minecraft:fire','minecraft:soul_fire','minecraft:lava','minecraft:campfire','minecraft:soul_campfire','minecraft:magma']);
const TUNDRA_BLOCKS=new Set(['minecraft:snow','minecraft:snow_layer','minecraft:snow_block','minecraft:powder_snow','minecraft:ice','minecraft:packed_ice','minecraft:blue_ice','minecraft:frosted_ice']);
const DANGEROUS_FOODS=new Set(['minecraft:rotten_flesh','minecraft:chicken','minecraft:poisonous_potato','minecraft:pufferfish','minecraft:spider_eye']);
const BITE_TIMES=Object.freeze({
 ONE:[1.16667,3.08333],TWO:[0.95833,4.0],THREE:[0.95833,2.33333,3.54167],THREE_ALT:[0.95833,2.16667,3.5],FOUR:[0.95833,2.33333,3.45833,4.08333]
});
const NUMB_VISUAL=new Set(),DRAGON_REPLAY=new Set(),DRAGON_PENDING=new Map();
const STORAGE_SORT_BLOCKS=new Set(['minecraft:chest','minecraft:trapped_chest','minecraft:barrel']);
const DRAGON_POOL_KEY='kaleidoscope_grilling:dragon_pool';
const OIL_TYPES=Object.freeze({canola:{heatTicks:1200},secret_chili:{heatTicks:12000},premium_chili:{heatTicks:24000}});
function writeTickState(block,before,next){
 const state=normalizeState(next),beforeState=normalizeState(before);
 const same=beforeState.phase===state.phase&&beforeState.phaseTicks===state.phaseTicks&&beforeState.flips===state.flips&&beforeState.flipCooldown===state.flipCooldown&&beforeState.seasoned===state.seasoned&&beforeState.failed===state.failed&&beforeState.heatTicks===state.heatTicks&&beforeState.lit===state.lit&&beforeState.seasonings.length===state.seasonings.length&&beforeState.seasonings.every((x,i)=>x===state.seasonings[i]);
 if(!same)world.setDynamicProperty(stateKey(block),JSON.stringify(state));
 // Java updateShape changes LEGGED when support below changes. Keep that visual/support sync live even on an otherwise idle grill.
 syncGrillPermutation(block,state);
 return state;
}
function soundFor(profile){return profile==='ONE'?'one_skewer_eat':profile==='TWO'?'two_skewer_eat':profile==='FOUR'?'four_skewer_eat':'three_skewer_eat'}
function stopEatSound(player,profile){stopSoundHandle(ACTIVE_EATS.get(player.id)?.audio)}
function spawnBiteCrumbs(player){
 try{
  const h=player.getHeadLocation(),v=player.getViewDirection();
  for(let i=0;i<5;i++)player.dimension.spawnParticle('kaleidoscope_grilling:skewer_crumb',{x:h.x+v.x*.32+(Math.random()-.5)*.14,y:h.y-.08+(Math.random()-.5)*.12,z:h.z+v.z*.32+(Math.random()-.5)*.14});
 }catch{}
}
function advanceBites(player,a){
 const elapsed=(system.currentTick-a.start)/20,times=a.biteTimes??[];
 while((a.nextBite??0)<times.length&&elapsed+1e-6>=times[a.nextBite]){spawnBiteCrumbs(player);a.nextBite++}
}


function now(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
const message=interactionFeedback;
function inv(block){return stationContainer(block)}
function grillDirection(block){
 try{const d=String(block.permutation.getState('minecraft:cardinal_direction')??'north');return ['north','south','west','east'].includes(d)?d:'north'}catch{return 'north'}
}
function removeGrillLegs(block){
 try{const below=block.below();if(below?.typeId===GRILL_LEGS_ID)below.setType('minecraft:air')}catch{}
}
function ensureGrillLegs(block){
 try{
  const below=block.below();if(!below)return false;
  if(below.typeId!==GRILL_LEGS_ID&&below.typeId!=='minecraft:air')return false;
  if(below.typeId==='minecraft:air')below.setType(GRILL_LEGS_ID);
  let p=below.permutation,dir=grillDirection(block);
  if(p.getState('kaleidoscope_grilling:direction')!==dir)below.setPermutation(p.withState('kaleidoscope_grilling:direction',dir));
  return true;
 }catch{return false}
}
function syncGrillPermutation(block,state){
 try{
  let below=block.below(),helper=below?.typeId===GRILL_LEGS_ID,supported=!helper&&(hasSolidTop(below)),legged=!supported,lit=!!state.lit;
  if(legged)ensureGrillLegs(block);else removeGrillLegs(block);
  let perm=block.permutation,changed=false;
  if(perm.getState('kaleidoscope_grilling:legged')!==legged){perm=perm.withState('kaleidoscope_grilling:legged',legged);changed=true}
  if(perm.getState('kaleidoscope_grilling:lit')!==lit){perm=perm.withState('kaleidoscope_grilling:lit',lit);changed=true}
  if(changed)block.setPermutation(perm);
 }catch{}
}
function writeState(block,s){const state=normalizeState(s);world.setDynamicProperty(stateKey(block),JSON.stringify(state));syncGrillPermutation(block,state)}
function clearState(block){world.setDynamicProperty(stateKey(block))}
function key(block){const p=block.location;return [block.dimension.id,p.x,p.y,p.z].join('|')}
function decrementHand(player,hand,count=1){
 if(creative(player))return true;const s=heldByHand(player,hand);if(!s||s.amount<count)return false;
 if(s.amount===count)setHand(player,hand,undefined);else{s.amount-=count;setHand(player,hand,s)}return true;
}
function decrementMain(player,count=1){return decrementHand(player,'main',count)}
function planDamagedHand(player,hand,amount=1){
 const stack=heldByHand(player,hand);if(!stack)return {ok:false,reason:'missing'};
 const before=stack.clone();
 if(creative(player))return {ok:true,before,next:before.clone(),mutate:false,broken:false};
 try{
  const durability=stack.getComponent('minecraft:durability');if(!durability)return {ok:false,reason:'not_durable'};
  const plan=nextDurability(durability.damage,durability.maxDurability,amount,!!durability.unbreakable);
  if(plan.broken)return {ok:true,before,next:undefined,mutate:true,broken:true};
  const next=stack.clone(),d=next.getComponent('minecraft:durability');if(!d)return {ok:false,reason:'not_durable'};
  d.damage=plan.damage;return {ok:true,before,next,mutate:true,broken:false};
 }catch{return {ok:false,reason:'durability_error'}}
}
function transactionStatus(result,label){
 if(!result.ok)console.warn('[Grilling '+label+'] '+String(result.error)+'; rollback failures='+result.rollbackErrors);
 return result.ok;
}
function commitGrillAndHand(block,beforeState,nextState,player,hand,beforeStack,nextStack,mutateHand=true){
 const storage=captureWritableHand(player,hand),mutate=mutateHand&&!creative(player);
 return commitStationTransfer(block,[
  {apply:()=>writeState(block,nextState),rollback:()=>writeState(block,beforeState)},
  {apply:()=>{if(mutate)storage.write(nextStack)},rollback:()=>{if(mutate)storage.write(storage.before)}}
 ],'grill/hand').ok;
}
function reducedStack(stack,count=1){
 if(!stack||stack.amount<count)throw new Error('Grilling: insufficient input');
 if(stack.amount===count)return undefined;
 const next=stack.clone();next.amount-=count;return next;
}
// A full inventory rejects threading/disassembly and restores both hands.
// Never gamble remaining ingredients on an unacknowledged world drop.
function prepareOutputDelivery(player,outputs){
 const container=mainContainer(player);if(!container)throw new Error('Grilling: output inventory unavailable');
 const before=Array.from({length:container.size},(_,i)=>container.getItem(i)?.clone());
 return {
  apply(){for(const output of outputs){const remaining=mergeIntoContainer(container,output,undefined,true);if(remaining)throw new Error('Grilling: make inventory space for remaining skewers/ingredients')}},
  rollback(){let failed=0;for(let i=0;i<before.length;i++)try{container.setItem(i,before[i])}catch{failed++}if(failed)throw new Error('Grilling: output rollback failed for '+failed+' writes');}
 };
}
function give(player,stack){const c=mainContainer(player);if(!c)return;const rem=mergeIntoContainer(c,stack);if(rem)player.dimension.spawnItem(rem,player.location)}
function copyOne(stack){const out=stack.clone();out.amount=1;return out}
function copyCustomData(from,to){
 try{if(from.nameTag)to.nameTag=from.nameTag}catch{}
 let lore=[];try{lore=getItemLore(from)}catch{}
 let ids=[];try{ids=getItemPropertyIds(from)}catch{}
 try{if(lore.length)setItemLore(to,lore);else if(ids.length)setItemLore(to,['§r'])}catch{}
 for(const id of ids)try{setItemProperty(to,id,getItemProperty(from,id))}catch{}
 return to;
}
function ingredientSnapshot(stack,full=false){
 let {nutrition,saturation,convertTo,edible}=foodFacts(stack);
 if(stack.typeId===SECRET_ID){const food=secretFood(readEffectiveSkewerRows(stack),isSecretCooked(stack),readSkewerRows(stack));nutrition=food.nutrition;saturation=food.saturation;edible=true;}
 let tags=[];try{tags=(stack.getTags?.()??[]).map(String).filter(x=>/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(x)).slice(0,64)}catch{}
 let lore=[];try{lore=getItemLore(stack)}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 const props=primitiveStackProps(stack),native=full?captureSkewerMetadata(stack):undefined;
 const signature=native?metadataSignature(native):JSON.stringify({id:stack.typeId,name,lore,props});
 return native?{id:stack.typeId,nutrition,saturation,convertTo,edible,tags,native}:{id:stack.typeId,nutrition,saturation,convertTo,edible,name,lore,props,tags,signature};
}
function restoreIngredient(row){
 if(row?.native&&row.native.id!==row.id)throw Error('Grilling: ingredient identity mismatch');
 if(row?.native)return restoreSkewerMetadata(row.native,(id,n)=>new ItemStack(id,n),id=>new EnchantmentType(id));
 const out=new ItemStack(row.id,1),props=row.props&&typeof row.props==='object'?row.props:{};
 if(row.name)out.nameTag=row.name;
 const lore=Array.isArray(row.lore)?row.lore:[];setItemLore(out,lore);
 for(const [id,value] of Object.entries(props))setItemProperty(out,id,value);
 if((out.nameTag??'')!==(row.name??'')||JSON.stringify(getItemLore(out))!==JSON.stringify(lore)||metadataSignature(primitiveStackProps(out))!==metadataSignature(props))throw Error('Grilling: legacy ingredient metadata readback differs');
 return out;
}
function behaviorRemainder(behavior){
 const spec=behavior?.remainder??(behavior?.convertTo?{id:behavior.convertTo,count:1}:undefined);
 if(!spec?.id)return undefined;
 let out;try{out=new ItemStack(spec.id,Math.max(1,Math.min(64,Number(spec.count)||1)))}catch{return undefined}
 try{if(spec.name)out.nameTag=spec.name}catch{}
 const props=spec.props&&typeof spec.props==='object'?spec.props:{},keys=Object.keys(props);
 try{if(Array.isArray(spec.lore)&&spec.lore.length)setItemLore(out,spec.lore);else if(keys.length)setItemLore(out,['§r'])}catch{}
 for(const id of keys)try{setItemProperty(out,id,props[id])}catch{}
 return out;
}
function readRowsFromKey(stack,key){
 const raw=getItemProperty(stack,key);if(raw===undefined)return [];
 if(typeof raw!=='string')throw Error('Grilling: invalid ingredient data');
 const rows=JSON.parse(raw);
 if(!Array.isArray(rows)||rows.length>3||rows.some(x=>!x||typeof x.id!=='string'))throw Error('Grilling: invalid ingredient rows');
 return rows;
}
function readSkewerRows(stack){return readRowsFromKey(stack,SKEWER_INGREDIENTS_KEY)}
function isSecretCooked(stack){try{return stack?.typeId===SECRET_ID&&getItemProperty(stack,SECRET_COOKED_KEY)===true}catch{return false}}
function readEffectiveSkewerRows(stack){if(isSecretCooked(stack)){const cooked=readRowsFromKey(stack,SECRET_COOKED_INGREDIENTS_KEY);if(cooked.length)return cooked}return readSkewerRows(stack)}
function rowLabel(row){return String(row.id??'').replace(/^.*:/,'').replaceAll('_',' ')}
function writeSkewerRows(stack,rows){
 const clean=(rows??[]).filter(x=>x&&typeof x.id==='string').slice(0,3);
 try{
  setItemLore(stack,['§8手工穿串 '+clean.length+'/3',...clean.map(x=>'§7- '+rowLabel(x))]);
  setItemProperty(stack,SKEWER_INGREDIENTS_KEY,JSON.stringify(clean));
 }catch{}
 return stack;
}
function setSecretCreator(stack,player){
 try{const creator={name:player.name,id:player.id};setItemProperty(stack,SECRET_CREATOR_KEY,JSON.stringify(creator));const lore=getItemLore(stack);lore.push('§7製作者: '+player.name);setItemLore(stack,lore)}catch{}
 return stack;
}
function cookedIngredientRows(rows){
 return (rows??[]).map(row=>{const id=resolveSecretSmokedId(row);if(!id)return row;try{const result=ingredientSnapshot(new ItemStack(id,1),true);return result.edible?result:row}catch{return row}});
}
function setCookedIngredientRows(stack,rows){if(readRowsFromKey(stack,SECRET_COOKED_INGREDIENTS_KEY).length===3)return stack;const value=JSON.stringify(cookedIngredientRows(rows));setItemProperty(stack,SECRET_COOKED_INGREDIENTS_KEY,value);if(getItemProperty(stack,SECRET_COOKED_INGREDIENTS_KEY)!==value)throw Error('Grilling: cooked ingredient data was not saved');return stack}
function dynamicFood(stack){return stack?.typeId===SECRET_ID?secretFood(readEffectiveSkewerRows(stack),isSecretCooked(stack),readSkewerRows(stack)):FOOD_DATA[stack?.typeId]}
function isEdible(stack){if(stack?.typeId==='kaleidoscope_grilling:sweet_potato_powder')return false;try{return foodFacts(stack).edible}catch{return false}}
function threadOutcome(player){
 const food=heldMain(player),off=heldOff(player);if(!food||!off||player.isSneaking)return null;
 if(off.typeId!=='minecraft:stick'&&off.typeId!==UNFINISHED_ID&&!(off.typeId===SECRET_ID&&!isSecretCooked(off)))return null;
 const rows=off.typeId==='minecraft:stick'?[]:readSkewerRows(off);
 const identity=ingredientSnapshot(food);
 const configured=canAppendConfigured(rows,identity)||isConfiguredIngredient(identity);
 let explicitAllow=false;
 if(!configured){
  const decision=skewerIngredientDecision(identity);
  if(decision==='deny')return null;
  explicitAllow=decision==='allow';
 }
 return appendOutcome(rows,identity,isEdible(food),explicitAllow);
}
function canDisassembleOff(player){const off=heldOff(player);return !!off&&isDisassemblableRaw(off.typeId,isSecretCooked(off))&&(off.typeId===UNFINISHED_ID||readSkewerRows(off).length>0)}
function threadCurrent(player){
 const main=captureWritableHand(player,'main'),other=captureWritableHand(player,'off');
 const food=main.before,off=other.before,outcome=threadOutcome(player);if(!food||!off||!outcome?.ok)return false;
 const rows=off.typeId==='minecraft:stick'?[]:readSkewerRows(off),nextRows=[...rows,ingredientSnapshot(food,true)],next=new ItemStack(outcome.id,1);
 restoreIngredient(nextRows[nextRows.length-1]); // Verify reconstructibility before either input is debited.
 writeSkewerRows(next,nextRows);if(outcome.kind==='secret')setSecretCreator(next,player);
 if(getItemProperty(next,SKEWER_INGREDIENTS_KEY)!==JSON.stringify(nextRows))throw new Error('Grilling: skewer data was not saved');
 if(outcome.kind==='secret'&&!getItemProperty(next,SECRET_CREATOR_KEY))throw new Error('Grilling: creator data was not saved');
 const free=creative(player),nextMain=free?food:reducedStack(food),outputs=[];
 // One result replaces one input; retain all other native input stacks.
 const starter=off.typeId==='minecraft:stick'||(off.typeId===UNFINISHED_ID&&rows.length===0);
 const keep=off.amount-(free&&starter?0:1);
 if(keep>0){const remaining=off.clone();remaining.amount=keep;outputs.push(remaining)}
 const delivery=outputs.length?prepareOutputDelivery(player,outputs):null;
 const steps=[
  {apply(){if(!free)main.write(nextMain)},rollback(){if(!free)main.write(food)}},
  {apply(){other.write(next)},rollback(){other.write(off)}}
 ];
 if(delivery)steps.push(delivery);
 if(!transactionStatus(commitSteps(steps),'threading')){interactionFailure(player,'§c穿串失敗，已嘗試回復原料');return false}
 useSound(player,'pickup_item',.7,1.2);
 awardLookingThePart(player,outcome);
 return true;
}
function disassembleOff(player){
 const other=captureWritableHand(player,'off'),off=other.before;if(!off||!canDisassembleOff(player))return false;
 const rows=readSkewerRows(off),outputs=rows.map(restoreIngredient);
 if(outputs.some(item=>!item))throw new Error('Grilling: an ingredient cannot be restored');
 outputs.push(new ItemStack('minecraft:stick',1));
 const delivery=prepareOutputDelivery(player,outputs),next=reducedStack(off);
 if(!transactionStatus(commitSteps([
  {apply(){other.write(next)},rollback(){other.write(off)}},delivery
 ]),'disassembly')){interactionFailure(player,'§c拆串失敗，已嘗試回復原料');return false}
 useSound(player,'skewer_disassemble',.8);
 return true;
}
function scheduleSkewerAction(player,action){
 const id=player.id,old=THREAD_LAST.get(id);if(old?.tick===system.currentTick)return true;
 const intent=captureTwoHandIntent(player);if(!intent)return false;
 const operation={tick:system.currentTick,action,intent};THREAD_LAST.set(id,operation);
 system.run(()=>{
  if(THREAD_LAST.get(id)!==operation||!twoHandIntentStillCurrent(player,intent))return;
  try{if(action==='disassemble')disassembleOff(player);else threadCurrent(player)}
  catch(error){console.warn('[Grilling skewer action] '+error);try{interactionFailure(player,'§c操作未完成；請確認原料與副手狀態')}catch{}}
 });return true;
}
function skewerAction(player,itemStack){
 if(player.isSneaking&&canDisassembleOff(player))return 'disassemble';
 const main=heldMain(player);if(!main||!itemStack||itemStack.typeId!==main.typeId)return null;
 return threadOutcome(player)?.ok?'thread':null;
}
function secretRemainders(player,stack){
 for(const row of readEffectiveSkewerRows(stack)){
  const behavior=rolledIngredientEffects(row);
  for(const e of behavior.effects){
   if(e.kind==='persistent_fx'){
    const old=fxGet(player,e.effect);fxSet(player,e.effect,Math.max(e.ticks,(old?.until??now())-now()),Math.max(e.amplifier??0,old?.amp??0));
   }else try{player.addEffect(e.effect,e.ticks,{...(e.options??{}),amplifier:e.amplifier??0,showParticles:true})}catch{}
  }
  if(behavior.clearPoison)try{player.removeEffect('poison')}catch{}
  if(behavior.ordinary)applyOrdinary(player);
  // Chorus fruit: bounded safe destinations with solid ground, like vanilla attempts.
  if(behavior.teleport){
   const from=player.location;
   for(let i=0;i<16;i++)try{
    let to={x:from.x+(Math.random()-.5)*16,y:Math.floor(from.y)+(Math.floor(Math.random()*16)-8),z:from.z+(Math.random()-.5)*16};
    for(let down=0;down<16;down++,to.y--){
     const below=player.dimension.getBlock({x:Math.floor(to.x),y:to.y-1,z:Math.floor(to.z)});
     if(hasSolidTop(below)){if(player.tryTeleport(to,{checkForBlocks:true})){player.dimension.playSound('mob.endermen.portal',to);i=16}break}
    }
   }catch{}
  }
  dangerousPreservation(player,row.id);
  if(behavior.damage>0)try{player.applyDamage(behavior.damage,{cause:'magic'})}catch{}
  const remainder=behaviorRemainder(behavior);if(remainder)give(player,remainder);
  for(const spec of behavior.remainders??[]){const extra=behaviorRemainder({remainder:spec});if(extra)give(player,extra);}
  emitSecretIngredientConsumed(player,row);
 }
}
function addSecretNutrition(player,stack,meta){
 const d=dynamicFood(stack),h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!d||!h||!sat)return;
 const hunger=Math.min(h.effectiveMax,h.currentValue+d.nutrition);h.setCurrentValue(hunger);
 const gain=d.nutrition*d.saturation*2*(meta?.hot?1.25:1);sat.setCurrentValue(Math.min(hunger,sat.currentValue+gain));
}
function addNestedNutrition(player,stack,meta){addSecretNutrition(player,stack,meta)}
function clearContainer(block){const c=inv(block);if(c)for(let i=0;i<3;i++)c.setItem(i,undefined)}
function resetBlock(block,lit=false){const s=initialState();s.lit=lit;writeState(block,s)}
function getUses(stack){try{return Math.max(0,Math.min(SEASONING_MAX_USES,Number(getItemProperty(stack,SEASON_USES_KEY)??0)|0))}catch{return 0}}
function setUses(stack,n){try{setItemProperty(stack,SEASON_USES_KEY,Math.max(0,Math.min(SEASONING_MAX_USES,n|0)))}catch{}return stack}
function cookedStack(raw,state){
 let stack;
 if(raw.typeId===SECRET_ID){
  stack=copyOne(raw);setCookedIngredientRows(stack,readSkewerRows(raw));setItemProperty(stack,SECRET_COOKED_KEY,true);if(!isSecretCooked(stack))throw Error('Grilling: cooked state was not saved');
 }else{
  const out=customSkewerCookedId(ingredientSnapshot(raw))||RAW_TO_COOKED[raw.typeId];
  if(!out)return new ItemStack(MYSTERIOUS_ID,1);
  stack=new ItemStack(out,1);copyCustomData(raw,stack);
 }
 setHot(stack,state.heatTicks);setSeasonings(stack,state.seasonings??[]);
 try{setItemProperty(stack,'kaleidoscope_grilling:seasoned',state.seasoned)}catch{}
 return refreshHotLore(stack);
}
function failedStack(raw,id){const stack=new ItemStack(id,1);return copyCustomData(raw,stack)}
function outputFor(raw,state,kind){if(kind==='raw')return copyOne(raw);if(kind==='dark')return failedStack(raw,DARK_ID);if(kind==='mysterious')return failedStack(raw,MYSTERIOUS_ID);return cookedStack(raw,state)}
function firstEmptyPlayerSlot(player){
 const c=mainContainer(player);if(!c)return -1;
 for(let i=0;i<c.size;i++)if(!c.getItem(i))return i;
 return -1;
}
function extract(block,player,all=false){
 const state=readState(block);if(!canExtract(state))return 0;const c=inv(block);if(!c)return 0;
 const rows=[];for(let i=0;i<3;i++){const raw=c.getItem(i);if(!raw)continue;rows.push({slot:i,output:outputFor(raw,state,outputKind(state))});if(!all)break;}
 if(!rows.length)return 0;
 const target=mainContainer(player);if(!target)throw new Error('Grilling: output inventory unavailable');
 const empty=[];for(let i=0;i<target.size;i++)if(!target.getItem(i))empty.push(i);
 const steps=rows.map(row=>slotWrite(c,row.slot,undefined));
 for(const row of rows){const slot=empty.shift();steps.push(slot!==undefined?slotWrite(target,slot,row.output):acknowledgedDrop(player.dimension,row.output,player.location));}
 if(rows.length===occupied(block))steps.push({apply:()=>resetBlock(block,state.lit),rollback:()=>writeState(block,state)});
 const result=commitStationTransfer(block,steps,'extract');
 if(!result.ok){interactionFailure(player,'§c取串失敗；已回復可確認的內容，請查看紀錄');return 0}
 blockSound(block,'pickup_item',.8);
 return rows.length;
}
function removeEscrow(entities){let ok=true;for(const e of entities)try{e?.remove()}catch{ok=false}return ok}
function restoreBrokenGrill(dim,loc,permutation,state,raws){
 try{
  let b=dim.getBlock(loc);if(!b)return;
  b.setPermutation(permutation);b=dim.getBlock(loc)??b;
  const c=inv(b);if(c)for(let i=0;i<3;i++)c.setItem(i,raws[i]);
  writeState(b,state);return true;
 }catch{return false}
}
function customBreak(block,player){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;
 const state=readState(block),kind=breakDisposition(state),c=inv(block),dim=block.dimension,loc={...block.location},permutation=block.permutation;
 if(!c){interactionFailure(player,'§c烤架庫存暫不可用，未拆除');return}
 const raws=[0,1,2].map(i=>c.getItem(i)),drops=[];
 try{
  for(const raw of raws)if(raw)drops.push(outputFor(raw,state,kind));
  if(!creative(player))drops.push(new ItemStack(GRILL_ID,1));
 }catch{interactionFailure(player,'§c拆除失敗：無法建立掉落物');return}
 const steps=drops.map((drop,i)=>acknowledgedDrop(dim,drop,{x:loc.x+.5,y:loc.y+(i===drops.length-1&&!creative(player)?.3:.4),z:loc.z+.5}));
 steps.push({apply(){clearContainer(block);clearState(block);removeGrillLegs(block);block.setType('minecraft:air')},rollback(){if(!restoreBrokenGrill(dim,loc,permutation,state,raws))throw new Error('Grill restore incomplete')}});
 if(!commitStationTransfer(block,steps,'break').ok){interactionFailure(player,'§c拆除失敗；已回復可確認的內容，請查看紀錄');return}
 try{removeGrillAudio(block)}catch{}
 try{retireEmptyStationContainer(dim.getBlock(loc))}catch(error){console.warn('[Grilling storage retirement] '+error)}
}
function heatForOil(type){return OIL_TYPES[type]?.heatTicks??OIL_TYPES.canola.heatTicks}
function planCookeryOil(player,hand,needed){
 const stack=heldByHand(player,hand),oil=planCookeryOilPotConsumption(stack,needed);
 if(!oil.ok)return oil;
 const heat=heatForOil(oil.type);
 if(creative(player))return {...oil,heat,remaining:oil.count,next:oil.before.clone(),mutate:false};
 return {...oil,heat,mutate:true};
}
function planSeasoningBottle(player,hand,needed){
 const stack=heldByHand(player,hand);if(!isSpecialSeasoningId(stack?.typeId))return {ok:false,reason:'not_seasoning'};
 const uses=getUses(stack),remaining=16-uses;if(remaining<needed)return {ok:false,reason:'insufficient',remaining};
 const ingredients=readSeasonings(stack),before=stack.clone();
 if(creative(player))return {ok:true,ingredients,uses,before,next:before.clone(),mutate:false};
 const nextUses=uses+needed;
 if(nextUses>=16)return {ok:true,ingredients,uses:nextUses,before,next:new ItemStack(EMPTY_SEASONING_ID,1),mutate:true};
 const next=retargetSpecialSeasoningStack(stack,nextUses,specialSeasoningVariant(stack));if(!next)return {ok:false,reason:'visual_state'};setUses(next,nextUses);try{setItemLore(next,['§7Uses: '+(16-nextUses)+'/16'])}catch{}
 return {ok:true,ingredients,uses:nextUses,before,next,mutate:true};
}
function handleGrill(block,player,hand='main'){
 if(!block?.isValid||block.typeId!==GRILL_ID)return;let state=readState(block);const held=heldByHand(player,hand),id=held?.typeId,n=occupied(block);
 if(id==='minecraft:flint_and_steel'){
  if(!state.lit){
   const tool=planDamagedHand(player,hand,1),nextState=light(state,true);
   if(!tool.ok){interactionFailure(player,'§c點火失敗：打火石狀態無法提交');return}
   if(!commitGrillAndHand(block,state,nextState,player,hand,tool.before,tool.next,tool.mutate)){interactionFailure(player,'§c點火交易失敗，已嘗試回滾');return}
   if(tool.broken)try{player.playSound('random.break',{volume:.8,pitch:1})}catch{}
   try{block.dimension.playSound('fire.ignite',block.location)}catch{}
  }
  return
 }
 if(isExtinguishTool(id)&&state.lit){
  state=light(state,false);writeState(block,state);try{block.dimension.playSound('random.fizz',block.location)}catch{}return
 }
 if(id===COOKERY_FILLED){
  if(!ensureOilHandPublished(player,hand,()=>handleGrill(block,player,hand)))return;
  if(state.phase!==0||n<1){javaInteractionFeedback(player,'no_brushable_skewers');return}
  const oil=planCookeryOil(player,hand,n);if(!oil.ok){javaInteractionFeedback(player,oil.reason==='insufficient'?'not_enough_oil':'no_brushable_skewers');return}
  const result=brush(state,n,oil.heat);
  if(result.ok){
   if(!commitGrillAndHand(block,state,result.state,player,hand,oil.before,oil.next,oil.mutate)){interactionFailure(player,'§c刷油交易失敗，油與烤架已嘗試回滾');return}
   awardGleamingWithOil(player);javaInteractionFeedback(player,'oiled',[n]);
   blockSound(block,'action_success',.65);
   try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}
  }return;
 }
 if(id&&Object.hasOwn(OIL_TOOLS,id)){const result=brush(state,n,OIL_TOOLS[id]);if(result.ok){writeState(block,result.state);awardGleamingWithOil(player);blockSound(block,'action_success',.65);try{player.playAnimation('animation.kg_imm.player.brush.'+hand,{blendOutTime:.12})}catch{}}return}
 if(isSpecialSeasoningId(id)){
  if(state.phase!==2||state.seasoned||n<1){javaInteractionFeedback(player,'no_seasonable_skewers');return}
  const bottle=planSeasoningBottle(player,hand,n);if(!bottle.ok){javaInteractionFeedback(player,bottle.reason==='insufficient'?'not_enough_seasoning':'no_seasonable_skewers');return}
  const result=season(state,n,bottle.ingredients);
  if(result.ok){
   if(!commitGrillAndHand(block,state,result.state,player,hand,bottle.before,bottle.next,bottle.mutate)){interactionFailure(player,'§c撒料交易失敗，調料與烤架已嘗試回滾');return}
   javaInteractionFeedback(player,'grill_ready_to_take',[],true);blockSound(block,'season',.85);
   try{player.playAnimation('animation.kg_imm.player.season.'+hand,{blendOutTime:.12})}catch{}
  }return;
 }
 if(id&&(Object.hasOwn(RAW_TO_COOKED,id)||isCompatRawSkewer(ingredientSnapshot(held))||(id===SECRET_ID&&!isSecretCooked(held)&&readSkewerRows(held).length===3))){
  if(!state.lit){javaInteractionFeedback(player,'grill_need_heat');return}if(!canInsert(state,n)){message(player,'§7烤爐現在不能再放入生串');return}
  const c=inv(block);if(!c)return;const slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;
  const storage=captureWritableHand(player,hand),free=creative(player),next=free?storage.before:reducedStack(storage.before),inserted=copyOne(storage.before);
  const result=commitTwoParty(
   ()=>c.setItem(slot,inserted),()=>{if(!free)storage.write(next)},
   ()=>c.setItem(slot,undefined),()=>{if(!free)storage.write(storage.before)}
  );
  if(!result.ok&&result.rollbackErrors)quarantineStation(block,'insert skewer rollback incomplete');
  if(!transactionStatus(result,'insert skewer'))interactionFailure(player,'§c插串失敗，已嘗試回復烤架與原料');
  else blockSound(block,'grill_flip',.75);
  return
 }
 if(id){message(player,'§7這個物品不能用在目前的烤爐階段');return}
 if(state.phase===1){const r=flip(state);if(r.ok){writeState(block,r.state);javaInteractionFeedback(player,'grill_wait_flip',[r.state.flips,4]);blockSound(block,'grill_flip',.75);try{player.playAnimation('animation.kg_imm.player.reach.'+hand,{blendOutTime:.1})}catch{}}else message(player,'§7翻面冷卻中');return}
 if(state.phase===0&&n>0){javaInteractionFeedback(player,'grill_need_oil');return}if(state.phase===2&&!state.seasoned){javaInteractionFeedback(player,'grill_need_seasoning');return}
 if(canExtract(state))extract(block,player,player.isSneaking)
}
function bottleDataFromItem(stack){
 if(!isNativeBottleItem(stack))throw new Error('Unknown item cannot become a seasoning bottle');
 const kind=isSpecialSeasoningId(stack?.typeId)?'special':stack?.typeId===PENDING_SEASONING?'pending':'empty';
 return {kind,ingredients:readSeasonings(stack),uses:kind==='special'?getUses(stack):0,variant:kind==='special'?specialSeasoningVariant(stack):0};
}
function bottleItem(data){
 const id=data.kind==='special'?specialSeasoningVisualId(data.uses??0,data.variant??0):data.kind==='pending'?PENDING_SEASONING:EMPTY_SEASONING_ID,stack=new ItemStack(id,1);setSeasonings(stack,data.ingredients??[]);
 if(data.kind==='special'){setUses(stack,data.uses??0);try{setItemProperty(stack,SEASON_VARIANT_KEY,data.variant??0);setItemLore(stack,['§7Uses: '+(SEASONING_MAX_USES-(data.uses??0))+'/'+SEASONING_MAX_USES,'§7Ingredients: '+(data.ingredients?.length??0)+'/'+SEASONING_CAPACITY])}catch{}}
 else try{if(data.ingredients?.length)setItemLore(stack,['§7Ingredients: '+data.ingredients.length+'/'+SEASONING_CAPACITY,data.kind==='pending'?'§eReady to shake':'§7Missing base seasoning'])}catch{}
 if(JSON.stringify(bottleDataFromItem(stack))!==JSON.stringify({kind:data.kind,ingredients:data.ingredients??[],uses:data.uses??0,variant:data.variant??0}))throw new Error('Bottle reconstruction did not preserve its mechanic fields');
 return stack;
}
function setBottleVisual(block,count){
 const target=count>0?'kaleidoscope_grilling:seasoning_bottle_'+Math.max(1,Math.min(SEASONING_MAX_BOTTLES,count)):'minecraft:air';
 if(block.typeId!==target)block.setType(target);
}
function nativeBottles(block,options){return readNativeBottles(block,bottleDataFromItem,bottleItem,options)}
function bottleRollbackStatus(block,result){
 if(result.rollbackErrors){
  try{quarantineStation(block,'bottle transaction rollback incomplete')}catch(error){console.warn('[Grilling bottle quarantine] '+error)}
  throw new Error('Bottle transaction recovery required; rollback incomplete');
 }
 return transactionStatus(result,'bottle/native-hand');
}
function bottleProjectionStep(block,items){
 const savedKey=seasoningBlockKey(block),savedRaw=world.getDynamicProperty(savedKey),rows=items.map(bottleDataFromItem);
 return {apply(){
  if(!writeBottleStack(block,rows))return false;
  return JSON.stringify(readBottleStack(block,true))===JSON.stringify(rows);
 },rollback(){world.setDynamicProperty(savedKey,savedRaw);markPlacedVisualDirty(block);return world.getDynamicProperty(savedKey)===savedRaw;}};
}
function commitBottleAndHand(block,current,nextItems,storage,nextHand,mutateHand=true){
 if(nextItems.length>SEASONING_MAX_BOTTLES||nextItems.some(x=>!isNativeBottleItem(x)||x.amount!==1))throw new Error('Invalid native bottle stack');
 const permutation=block.permutation;
 const result=commitSteps([
  ...Array.from({length:SEASONING_MAX_BOTTLES},(_,i)=>slotWrite(current.container,i,nextItems[i])),
  bottleProjectionStep(block,nextItems),
  {apply(){setBottleVisual(block,nextItems.length)},rollback(){block.setPermutation(permutation)}},
  {apply(){if(mutateHand)return storage.write(nextHand)},rollback(){if(mutateHand)return storage.write(storage.before)}}
 ]);
 const ok=bottleRollbackStatus(block,result);
 if(ok&&!nextItems.length)try{retireEmptyStationContainer(block)}catch(error){console.warn('[Grilling bottle empty storage retirement] '+error)}
 return ok;
}
function pushBottle(block,player,held,hand='main'){
 const current=nativeBottles(block);if(current.items.length>=SEASONING_MAX_BOTTLES){message(player,'§c最多只能堆'+SEASONING_MAX_BOTTLES+'瓶');return false}
 const storage=captureWritableHand(player,hand),free=creative(player),next=free?storage.before:reducedStack(storage.before);
 const items=[...current.items,copyOne(storage.before)];
 const ok=commitBottleAndHand(block,current,items,storage,next,!free);
 if(!ok)interactionFailure(player,'§c放瓶失敗，已嘗試回復調料與手持物品');
 else blockSound(block,'seasoning_bottle_stack',.8);return ok;
}
function handleSeasoningBlock(block,player,hand='main'){
 const current=nativeBottles(block),items=current.items.map(x=>x.clone());
 const held=heldByHand(player,hand),id=held?.typeId;
 if(id===EMPTY_SEASONING_ID||id===PENDING_SEASONING||isSpecialSeasoningId(id)){pushBottle(block,player,held,hand);return}
 const topItem=items.at(-1),top=bottleDataFromItem(topItem);
 if(id&&Object.hasOwn(SEASONING_KINDS,id)){
  if(top.kind==='special'){message(player,'§7最上層是完成調料，不能再加料');return}
  if(top.ingredients.length>=SEASONING_CAPACITY){javaInteractionFeedback(player,'bottle_full');return}
  const storage=captureWritableHand(player,hand),free=creative(player),next=free?storage.before:reducedStack(storage.before);
  top.ingredients.push(id);
  // Java mutates the existing stack, except the explicit EMPTY -> PENDING promotion.
  if(top.kind==='empty'&&hasSeasoningBase(top.ingredients))items[items.length-1]=bottleItem({...top,kind:'pending'});
  else{setSeasonings(topItem,top.ingredients);if(JSON.stringify(readSeasonings(topItem))!==JSON.stringify(top.ingredients))throw new Error('Bottle seasoning data write rejected');}
  if(!commitBottleAndHand(block,current,items,storage,next,!free)){interactionFailure(player,'§c加料失敗，已嘗試回復原料');return}
  awardSeasoningMilestones(player,top.ingredients);
  blockSound(block,'action_success',.8);
  try{block.dimension.spawnParticle('minecraft:endrod',{x:block.x+.5,y:block.y+.7,z:block.z+.5})}catch{}
  return;
 }
 if(!id){
  const storage=captureWritableHand(player,hand);let item=items.pop();const data=bottleDataFromItem(item);
  if(storage.before)throw new Error('Grilling: take-bottle hand is no longer empty');
  if(data.kind==='empty'&&hasSeasoningBase(data.ingredients))item=bottleItem({...data,kind:'pending'});
  if(!commitBottleAndHand(block,current,items,storage,item))interactionFailure(player,'§c取瓶失敗，已嘗試回復調料');
  else blockSound(block,'seasoning_bottle_stack',.8);
  return;
 }
 javaInteractionFeedback(player,'invalid_seasoning');
}
function sameBottleTarget(block,snapshot){
 return block&&block.typeId===snapshot.typeId&&Object.entries(snapshot.states).every(([key,value])=>block.permutation.getState(key)===value);
}
function bottleTargetSnapshot(block){return {typeId:block.typeId,states:block.permutation.getAllStates(),permutation:block.permutation}}
function bottleActionSnapshot(block){return {target:bottleTargetSnapshot(block),owner:world.getDynamicProperty(stationStorageKey(block)),projection:world.getDynamicProperty(seasoningBlockKey(block))}}
function bottleActionStillCurrent(block,captured){return sameBottleTarget(block,captured.target)&&world.getDynamicProperty(stationStorageKey(block))===captured.owner&&world.getDynamicProperty(seasoningBlockKey(block))===captured.projection}
function scheduleNativeBottlePlacement(e){
 if(e.cancel)return;e.cancel=true;
 const player=e.player;if(!player||e.face!=='Up')return;
 const mode=player.getGameMode();if(mode!==GameMode.Survival&&mode!==GameMode.Creative)return;
 const held=heldMain(player);if(!held||!(held.typeId===EMPTY_SEASONING_ID||held.typeId===PENDING_SEASONING||isSpecialSeasoningId(held.typeId)))return;
 const support=e.block.below();if(!hasSolidTop(support))return;
 const target=bottleTargetSnapshot(e.block),below=bottleTargetSnapshot(support),dimension=e.block.dimension,location={...e.block.location},proposed=e.permutationToPlace,intent=captureInteractionIntent(player,held);
 system.run(()=>{
  let block,current,freshPreflight=false;
  try{
   if(player.isValid===false||player.dimension.id!==dimension.id||!interactionIntentStillCurrent(player,intent))return;
   const mode=player.getGameMode();if(mode!==GameMode.Survival&&mode!==GameMode.Creative)return;
   if(Math.hypot(player.location.x-location.x-.5,player.location.y-location.y-.5,player.location.z-location.z-.5)>8)return;
   block=dimension.getBlock(location);if(!sameBottleTarget(block,target)||!sameBottleTarget(block.below(),below)||!hasSolidTop(block.below()))return;
   if(world.getDynamicProperty(seasoningBlockKey(block))!==undefined)throw new Error('Target has unresolved seasoning data');
   let presence=inspectStationStorage(block);if(presence.retiredEmpty){retireEmptyStationContainer(block);presence=inspectStationStorage(block);}
   if(presence.linked||presence.orphans||block.getComponent('minecraft:inventory')?.container)throw new Error('Target has unresolved native storage');
   freshPreflight=true;
   const storage=captureWritableHand(player,intent.hand),free=creative(player),item=copyOne(storage.before),next=free?storage.before:reducedStack(storage.before);
   const steps=[
    {apply(){block.setPermutation(proposed)},rollback(){block.setPermutation(target.permutation)}},
    {apply(){current=nativeBottles(block,{fresh:true})},rollback(){}},
    {apply(){return current.container.setItem(0,item.clone())},rollback(){if(current)return current.container.setItem(0,undefined)}},
    bottleProjectionStep(block,[item]),
    {apply(){if(!free)return storage.write(next)},rollback(){if(!free)return storage.write(storage.before)}}
   ];
   const result=commitSteps(steps);if(!result.ok){
    bottleRollbackStatus(block,result);
    if(current?.created||freshPreflight)try{retireEmptyStationContainer(block)}catch(error){console.warn('[Grilling bottle placement cleanup] '+error)}
   }else blockSound(block,'seasoning_bottle_place',.8);
  }catch(error){console.warn('[Grilling native bottle placement] '+error);}
 });
}
function scheduleNativeBottleBreak(e){
 if(e.cancel||!isSeasoningBlock(e.block.typeId))return;e.cancel=true;
 try{
  const dimension=e.block.dimension,location={...e.block.location},snapshot=bottleTargetSnapshot(e.block);
  const owner=world.getDynamicProperty(stationStorageKey(e.block)),projection=world.getDynamicProperty(seasoningBlockKey(e.block));
  system.run(()=>{try{
   const block=dimension.getBlock(location);
   if(!sameBottleTarget(block,snapshot)||world.getDynamicProperty(stationStorageKey(block))!==owner||world.getDynamicProperty(seasoningBlockKey(block))!==projection)return;
   breakNativeBottles(block);
  }catch(error){console.warn('[Grilling bottle break] '+error)}});
 }catch(error){console.warn('[Grilling bottle break capture] '+error)}
}
function breakNativeBottles(block,dropContents=true){
 if(!block||!isSeasoningBlock(block.typeId))return false;
 const current=nativeBottles(block),permutation=block.permutation,drops=[];
 const steps=(dropContents?current.items:[]).map(item=>{let entity,attempted=false;return {
  apply(){attempted=true;entity=block.dimension.spawnItem(item.clone(),{x:block.x+.5,y:block.y+.4,z:block.z+.5});if(!entity)throw new Error('Bottle drop not confirmed');drops.push(entity)},
  rollback(){if(entity)entity.remove();else if(attempted)throw new Error('Bottle drop outcome unknown; manual recovery required')}
 }});
 steps.push(...Array.from({length:SEASONING_MAX_BOTTLES},(_,i)=>slotWrite(current.container,i,undefined)),bottleProjectionStep(block,[]),
  {apply(){block.setType('minecraft:air')},rollback(){block.setPermutation(permutation)}});
 const result=commitSteps(steps);if(!bottleRollbackStatus(block,result))return false;
 try{retireEmptyStationContainer(block)}catch(error){console.warn('[Grilling bottle break storage retirement] '+error)}
 return true;
}
// Java support loss returns AIR without the playerWillDestroy payout. The
// backing inventory must follow that destructive lifecycle, not become orphaned.
function tickNativeBottleSupport(block){
 if(!block||!isSeasoningBlock(block.typeId))return;
 const below=block.below();if(!below||hasSolidTop(below))return;
 breakNativeBottles(block,false);
}
function scheduleNativeBottleExplosion(e){
 if(e.cancel)return;
 const pending=[],keep=[];
 for(const block of e.getImpactedBlocks()){
  if(isSeasoningBlock(block.typeId))pending.push({dimension:block.dimension,location:{...block.location},captured:bottleActionSnapshot(block)});
  else keep.push(block);
 }
 if(!pending.length)return;e.setImpactedBlocks(keep);
 system.run(()=>{for(const row of pending)try{
  const block=row.dimension.getBlock(row.location);
  if(bottleActionStillCurrent(block,row.captured))breakNativeBottles(block,false);
 }catch(error){console.warn('[Grilling bottle explosion recovery] '+error)}});
}
function handleCustomBlockInteraction(block,player,intent){
 if(!block||(block.typeId!==GRILL_ID&&!isSeasoningBlock(block.typeId)))return;
 if(!interactionIntentStillCurrent(player,intent)){message(player,'§7操作已取消：互動後手持物品已改變');return}
 if(block.typeId===GRILL_ID)handleGrill(block,player,intent.hand);
 else handleSeasoningBlock(block,player,intent.hand);
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
function setDragonPool(entity,value){try{entity.setDynamicProperty(DRAGON_POOL_KEY,value===undefined?undefined:Math.max(0,Math.min(2,Number(value)||0)))}catch{}}
function applyDragonBlood(player,ticks,amp){
 const old=fxGet(player,'dragon_blood');amp=Math.max(amp,old?.amp??0);
 fxSet(player,'dragon_blood',Math.max(ticks,old?old.until-now():0),amp);
 if(!old)setDragonPool(player,2);
 try{player.addEffect('health_boost',Math.max(25,ticks),{amplifier:amp>0?1:0,showParticles:false})}catch{}
 const gain=dragonHealthGain(old?.amp,amp);
 if(gain>0)system.run(()=>{try{const hp=player.getComponent('minecraft:health');if(hp)hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+gain))}catch{}});
}

function applySeasoning(player,list){
 const c=counts(list);let duration=3600;if((c.duration??0)>=4)duration*=4;else if((c.duration??0)>0)duration*=2;
 if((c.speed??0)>0)try{player.addEffect('speed',duration,{amplifier:c.speed>=4?1:0,showParticles:true})}catch{}
 if((c.strength??0)>0)try{player.addEffect('strength',duration,{amplifier:c.strength>=4?1:0,showParticles:true})}catch{}
 if((c.numbness??0)>=4)fxSet(player,'numb',900*((c.duration??0)>=4?4:(c.duration??0)>0?2:1));
 if((c.totem??0)>0){
  const poisoned=!!fxGet(player,'heavy_metal_poisoning');
  if(poisoned)awardMetalToleranceFailed(player,c.totem,true);
  else fxSet(player,'heavy_metal',duration,c.totem>=4?1:0);
 }
 if((c.vitality??0)>0)applyDragonBlood(player,duration,c.vitality>=4?1:0);
}
function dangerousPreservation(player,itemId){if(!DANGEROUS_FOODS.has(itemId)||!fxGet(player,'preservation'))return;for(const id of ['hunger','poison','nausea'])try{player.removeEffect(id)}catch{}}
function applyOrdinary(player){
 const challenged=!!fxGet(player,'invincible');if(challenged)fxClear(player,'invincible');
 const outcome=ordinaryChallengeOutcome(challenged,Math.random());
 if(outcome==='shield'){awardOrdinaryChallenge(player,outcome);try{player.dimension.playSound('random.shield_block',player.location);player.dimension.spawnParticle('minecraft:electric_spark_particle',{x:player.location.x,y:player.location.y+1,z:player.location.z})}catch{}return}
 if(outcome==='spear')awardOrdinaryChallenge(player,outcome);
 system.run(()=>{try{player.kill()}catch{try{player.applyDamage(100000,{cause:'override'})}catch{}}});
}
function afterCommitted(player,id,meta,active,fullNative){
 applyFixedEffect(player,id);
 awardEatItHot(player,id,meta.hot);
 awardMentalPreparationFailed(player,id);
 if(meta.hot){doubleNewNative(player,active.nativeBefore);doubleNewFx(player,active.fxBefore)}
 if(meta.hot&&fullNative&&active.saturationBefore!==undefined){const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(h&&sat){const gained=Math.max(0,sat.currentValue-active.saturationBefore);sat.setCurrentValue(Math.min(h.currentValue,active.saturationBefore+gained*1.25))}}
 if(meta.hot)applySeasoning(player,meta.seasonings);
 if(id==='kaleidoscope_grilling:grilled_golden_skewer')try{player.dimension.playSound('beacon.power',player.location)}catch{}
 if(id==='kaleidoscope_grilling:ordinary_skewer')applyOrdinary(player);
}
function stackMeta(stack){return {hot:isHot(stack),seasonings:readSeasonings(stack),hotUntil:hotUntil(stack)}}
function hungerSettle(player,id,active){
 active={...active,meta:{...active.meta,hot:active.meta.hot&&active.meta.hotUntil>now()}};
 const current=heldByHand(player,active.hand);
 if(!current||current.typeId!==id||!eatingStillCurrent(active.use,current,player.selectedSlotIndex,now()))return false;
 const d=id===SECRET_ID?dynamicFood(current):FOOD_DATA[id],h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');
 if(!d||!h||!sat)return false;
 const consumed=copyOne(current),before=current.clone(),next=current.amount>1?current.clone():undefined;
 if(next)next.amount--;
 const oldH=h.currentValue,oldS=sat.currentValue,hunger=Math.min(h.effectiveMax,oldH+d.nutrition);
 const saturation=Math.min(hunger,oldS+d.nutrition*d.saturation*2*(active.meta.hot?1.25:1));
 const write=stack=>{
  if(active.hand==='off'){
   const eq=player.getComponent('minecraft:equippable');
   if(!eq||!eq.setEquipment(EquipmentSlot.Offhand,stack))throw new Error('Offhand unavailable');
  }else{
   const c=mainContainer(player);if(!c)throw new Error('Inventory unavailable');c.setItem(active.use.slot,stack);
  }
 };
 if(!commitEating({debit:()=>{if(!creative(player))write(next)},reward:()=>{h.setCurrentValue(hunger);sat.setCurrentValue(saturation)},
  restoreFood:()=>{if(!creative(player))write(before)},restoreNutrition:()=>{h.setCurrentValue(oldH);sat.setCurrentValue(oldS)}}))return false;

 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 if(id===SECRET_ID)secretRemainders(player,consumed);
 afterCommitted(player,id,active.meta,active,false);return true;
}
function resolvedProfile(profile){return profile==='THREE_RANDOM'?(Math.random()<.5?'THREE':'THREE_ALT'):profile}
function profileDuration(profile){return profile==='THREE'?100:90}
function writeUseHand(player,use,stack){
 if(use.hand==='off'){
  const eq=player.getComponent('minecraft:equippable');
  if(!eq||!eq.setEquipment(EquipmentSlot.Offhand,stack))throw new Error('Offhand unavailable');
 }else{
  const c=mainContainer(player);if(!c)throw new Error('Inventory unavailable');c.setItem(use.slot,stack);
 }
}
function completePlateUse(player,eventStack){
 const a=PLATE_EATS.get(player.id);PLATE_EATS.delete(player.id);
 if(!a||!completedUseStillCurrent(a.use,eventStack,heldByHand(player,a.hand),player.selectedSlotIndex,!creative(player)))return;
 let eaten,meta,next;
 const h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');
 try{
  if(!h||!sat)throw new Error('Nutrition unavailable');
  const rows=a25PlateRows(a.plate),index=plateHighestNutritionIndex(rows);
  if(index<0)throw new Error('Empty plate');
  const row=rows.splice(index,1)[0];eaten=a25RestoreStack(row);if(!eaten)throw new Error('Plate food unavailable');
  const restored=primitiveStackProps(eaten);
  for(const key of Object.keys(row.props??{}))if(JSON.stringify(restored[key])!==JSON.stringify(row.props[key]))throw new Error('Plate food metadata unavailable');
  meta=stackMeta(eaten);next=rows.length?a25PlateItem(rows,a.plate):undefined;
  if(rows.length&&(!next||JSON.stringify(a25PlateRows(next))!==JSON.stringify(rows)))throw new Error('Plate data write failed');
 }catch(error){writeUseHand(player,a.use,a.plate);console.warn('[Grilling plate] '+error);return}
 const oldH=h.currentValue,oldS=sat.currentValue;
 if(!commitEating({debit:()=>writeUseHand(player,a.use,next),reward:()=>addNestedNutrition(player,eaten,meta),
  restoreFood:()=>writeUseHand(player,a.use,a.plate),restoreNutrition:()=>{h.setCurrentValue(oldH);sat.setCurrentValue(oldS)}}))return;
 const id=eaten.typeId;dangerousPreservation(player,id);

 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 if(id===SECRET_ID)secretRemainders(player,eaten);
 afterCommitted(player,id,meta,{...a,meta},false);
}
function completePending(player,stack){
 const a=PENDING_USES.get(player.id);
 if(!a||!completedUseStillCurrent(a.use,stack,heldByHand(player,a.hand),player.selectedSlotIndex))return;
 PENDING_USES.delete(player.id);stopSoundHandle(a.audio);
 const list=readSeasonings(stack);if(!hasSeasoningBase(list)){javaInteractionFeedback(player,'missing_base_seasoning');return}
 const variant=Math.floor(Math.random()*(SEASONING_VARIANT_MAX+1)),out=new ItemStack(specialSeasoningVisualId(0,variant),1);setSeasonings(out,list);setUses(out,0);
 setItemProperty(out,SEASON_VARIANT_KEY,variant);setItemLore(out,['§7Uses: '+SEASONING_MAX_USES+'/'+SEASONING_MAX_USES,'§7Ingredients: '+list.length+'/'+SEASONING_CAPACITY]);
 if(JSON.stringify(readSeasonings(out))!==JSON.stringify(list)||getUses(out)!==0)throw new Error('Seasoning data write failed');
 if(commitEating({debit:()=>writeUseHand(player,a.use,out),reward:()=>{},restoreFood:()=>writeUseHand(player,a.use,a.stack),restoreNutrition:()=>{}})){seasoningFinished(player);awardSeasoningFinishedChallenges(player,list)}
}
world.afterEvents.itemStartUse.subscribe(e=>{
 const id=e.itemStack?.typeId;
 if(id===PENDING_SEASONING){const hand=captureInteractionIntent(e.source,e.itemStack).hand;
  stopSoundHandle(PENDING_USES.get(e.source.id)?.audio);
  PENDING_USES.set(e.source.id,{stack:e.itemStack.clone(),hand,use:captureEatingIdentity(e.itemStack,hand,e.source.selectedSlotIndex),audio:useSound(e.source,'shake_seasoning',.8)});
  try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 if(id===PLATE_ID){
  const rows=a25PlateRows(e.itemStack),index=plateHighestNutritionIndex(rows);if(index<0)return;
  const selected=a25RestoreStack(rows[index]),meta=stackMeta(selected),sat=e.source.getComponent('minecraft:player.saturation'),hand=captureInteractionIntent(e.source,e.itemStack).hand;
  PLATE_EATS.set(e.source.id,{id,plate:e.itemStack.clone(),hand,use:captureEatingIdentity(e.itemStack,hand,e.source.selectedSlotIndex),meta,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined});return;
 }
  if(CUISINE_FOOD_SET.has(id)){
   const meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');
   CUISINE_EATS.set(e.source.id,{id,meta,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined});
   return;
  }
  if(!FOOD_DATA[id]&&id!==SECRET_ID)return;
  const requested=PROFILE_BY_ITEM[id]??'THREE_RANDOM',hand=captureInteractionIntent(e.source,e.itemStack).hand,profile=resolvedProfile(requested),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');
 const a={id,start:system.currentTick,nativeDuration:Math.max(0,Number(e.useDuration)||0),requested,profile,hand,use:captureEatingIdentity(e.itemStack,hand,e.source.selectedSlotIndex),meta,biteTimes:BITE_TIMES[profile]??BITE_TIMES.THREE,nextBite:0,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined};
 stopSoundHandle(ACTIVE_EATS.get(e.source.id)?.audio);ACTIVE_EATS.set(e.source.id,a);
 // A284: minecraft:use_animation owns the eating pose in both views. The legacy
 // Java camera-space arm/item offsets detach third-person limbs and double-transform attachables.
 try{a.audio=e.source.playSound('kg_imm.'+soundFor(profile))}catch{}
});
world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 if(id===PLATE_ID){completePlateUse(e.source,e.itemStack);return}
  dangerousPreservation(e.source,id);
  if(CUISINE_FOOD_SET.has(id)){
   const a=CUISINE_EATS.get(e.source.id)??{id,meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};
   CUISINE_EATS.delete(e.source.id);afterCommitted(e.source,id,a.meta,a,true);return;
  }
  if(!FOOD_DATA[id]&&id!==SECRET_ID)return;
 const a=ACTIVE_EATS.get(e.source.id);
 if(!a||a.id!==id||!eatingEventMatches(a.use,e.itemStack,now())||system.currentTick-a.start<a.nativeDuration)return;
 a.meta={...a.meta,hot:a.meta.hot&&a.meta.hotUntil>now()};
 stopEatSound(e.source,a.profile);SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(id===SECRET_ID){addSecretNutrition(e.source,e.itemStack,{hot:false})}
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 if(id===SECRET_ID)secretRemainders(e.source,e.itemStack);
 afterCommitted(e.source,id,a.meta,a,true);
});
world.afterEvents.itemStopUse.subscribe(e=>{
 // Completion and stop can share a tick. Clear only the stopped session, after
 // completion has had a chance to commit; never delete a new use session.
 const id=e.source.id,plate=PLATE_EATS.get(id),pending=PENDING_USES.get(id);
 const pendingMatches=!e.itemStack||!pending||eatingEventMatches(pending.use,e.itemStack,now());
 system.run(()=>{if(PLATE_EATS.get(id)===plate)PLATE_EATS.delete(id);if(pendingMatches&&PENDING_USES.get(id)===pending){stopSoundHandle(pending?.audio);PENDING_USES.delete(id)}});
 CUISINE_EATS.delete(id);const a=ACTIVE_EATS.get(id);if(!a)return;
 if(e.itemStack&&!eatingEventMatches(a.use,e.itemStack,now()))return;
 if(a.start===system.currentTick&&SETTLED.get(id)===system.currentTick)return;
 const used=system.currentTick-a.start;stopEatSound(e.source,a.profile);
 // Let native completion win either event order; never delete a newer session.
 system.run(()=>{if(ACTIVE_EATS.get(id)!==a)return;ACTIVE_EATS.delete(id);if(e.itemStack&&used>=25&&hungerSettle(e.source,a.id,a))SETTLED.set(id,system.currentTick);});
});
// Native use poses cancel with the use action; no global zero-pose reset may override
// the next held item. Release server bookkeeping as well when a player disconnects.
world.afterEvents.playerLeave.subscribe(e=>{stopSoundHandle(PENDING_USES.get(e.playerId)?.audio);stopSoundHandle(ACTIVE_EATS.get(e.playerId)?.audio);for(const map of [ACTIVE_EATS,CUISINE_EATS,PLATE_EATS,PENDING_USES,SETTLED])map.delete(e.playerId)});
world.beforeEvents.entityHurt.subscribe(e=>{
 const target=e.hurtEntity,cause=e.damageSource?.cause;
 if(fxGet(target,'invincible')&&cause!=='selfDestruct'&&cause!=='override'){e.cancel=true;system.run(()=>{try{target.dimension.playSound('random.shield_block',target.location)}catch{}});return}
 if(e.damageSource?.damagingProjectile&&fxGet(target,'projectile_dodge')){e.cancel=true;system.run(()=>{fxReduce(target,'projectile_dodge',200);const base=target.location;for(let i=0;i<16;i++){const to={x:base.x+(Math.random()-.5)*3,y:base.y+(Math.random()-.5)*3,z:base.z+(Math.random()-.5)*3};try{if(target.tryTeleport(to,{checkForBlocks:true})){target.dimension.playSound('mob.endermen.portal',target.location);break}}catch{}}});return}
 const replay=DRAGON_REPLAY.delete(target.id);
 if(!replay){
  const db=fxGet(target,'dragon_blood'),pool=dragonPool(target),plan=planDragonDamage(pool,e.damage,DRAGON_PENDING.get(target.id)??0);
  if(db&&plan.absorbed>0){
   // beforeEvents is read-only. Reserve in memory now; persist in a mutable tick.
   DRAGON_PENDING.set(target.id,plan.pending);e.cancel=true;
   const source=e.damageSource;
   system.run(()=>{
    setDragonPool(target,dragonPool(target)-plan.absorbed);
    const left=Math.max(0,(DRAGON_PENDING.get(target.id)??0)-plan.absorbed);if(left)DRAGON_PENDING.set(target.id,left);else DRAGON_PENDING.delete(target.id);
    if(plan.remaining>0)try{DRAGON_REPLAY.add(target.id);const opt={cause:source?.cause??'entityAttack'};if(source?.damagingEntity)opt.damagingEntity=source.damagingEntity;target.applyDamage(plan.remaining,opt)}catch{DRAGON_REPLAY.delete(target.id)}
   });return;
  }
 }
 const hm=fxGet(target,'heavy_metal'),hp=target.getComponent?.('minecraft:health');if(hm&&!fxGet(target,'heavy_metal_poisoning')&&hp&&e.damage>=hp.currentValue){e.cancel=true;system.run(()=>{fxClear(target,'heavy_metal');fxSet(target,'heavy_metal_poisoning',12000);try{hp.setCurrentValue(1);target.dimension.playSound('random.totem',target.location)}catch{}})}
});
world.afterEvents.entityHitEntity.subscribe(e=>{if(fxGet(e.damagingEntity,'hinder'))try{e.hitEntity.addEffect('slowness',100,{amplifier:1,showParticles:true})}catch{}});
function canUseSecretSkewer(stack){
 try{const valid=rows=>rows.length===3&&rows.every(row=>/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(row.id)&&(!row.native||(row.native.version===1&&row.native.id===row.id)));return valid(readSkewerRows(stack))&&(!isSecretCooked(stack)||valid(readEffectiveSkewerRows(stack)))}catch{return false}
}
world.beforeEvents.itemUse.subscribe(e=>{
 if(e.cancel)return;
 if(e.itemStack?.typeId===SECRET_ID&&!canUseSecretSkewer(e.itemStack)){e.cancel=true;return}
 try{
  const action=skewerAction(e.source,e.itemStack);
  if(action){e.cancel=true;scheduleSkewerAction(e.source,action);return}
  if(e.source.isSneaking&&isHot(e.itemStack)&&!heldOff(e.source)&&isFoodStack(e.itemStack)){
   e.cancel=true;const p=e.source,intent=captureInteractionIntent(p,e.itemStack),sample=e.itemStack.clone();
   system.run(()=>{if(interactionIntentStillCurrent(p,intent)){const c=mainContainer(p);if(c)compactMatchingHotFood(c,sample)}});
  }
 }catch{}
});
world.beforeEvents.playerInteractWithEntity.subscribe(e=>{
 try{const action=skewerAction(e.player,e.itemStack??heldMain(e.player));if(!action)return;e.cancel=true;scheduleSkewerAction(e.player,action)}catch{}
});
// Stable Script API placement capture, including all materialized seasoning IDs.
system.beforeEvents.startup.subscribe(({blockComponentRegistry})=>{
 blockComponentRegistry.registerCustomComponent('kaleidoscope_grilling:grill_tick',{onTick(e){tickGrill(e.block);tickGrillDisplay(e.block)}});
 blockComponentRegistry.registerCustomComponent('kaleidoscope_grilling:grill_legs_tick',{onTick(e){try{const above=e.block.above();if(above&&above.typeId!==GRILL_ID)e.block.setType('minecraft:air')}catch{}}});
 blockComponentRegistry.registerCustomComponent('senluo:grilling_bottle_place',{beforeOnPlayerPlace:scheduleNativeBottlePlacement,onTick(e){try{tickNativeBottleSupport(e.block)}catch(error){console.warn('[Grilling bottle support recovery] '+error)}}});
});
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(e.cancel)return;
 if(tryScheduleBeefBoardOverride(e))return;
 const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));
 if(skewerInput){e.cancel=true;if(isInitialBlockPress(e.isFirstEvent))scheduleSkewerAction(e.player,skewerInput);return}
 const grillTarget=e.block.typeId===GRILL_ID,customTarget=grillTarget||isSeasoningBlock(e.block.typeId);
 const sortTarget=e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId);
 if(!isInitialBlockPress(e.isFirstEvent)){if(customTarget||sortTarget)e.cancel=true;return}
 if(sortTarget){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;compactSkewerContainer(c,false)});return;
 }
 if(!customTarget)return;
 e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension,intent=customTarget?captureInteractionIntent(p,e.itemStack):null,bottleCapture=isSeasoningBlock(e.block.typeId)?bottleActionSnapshot(e.block):undefined;
 system.run(()=>{try{const target=dim.getBlock(loc);if(bottleCapture&&!bottleActionStillCurrent(target,bottleCapture))return;handleCustomBlockInteraction(target,p,intent)}catch(error){console.warn('[Grilling block action] '+error);try{interactionFailure(p,'§c操作未完成；請查看紀錄並核對原料')}catch{}}});
});
world.afterEvents.playerPlaceBlock.subscribe(e=>{if(e.block.typeId===GRILL_ID)resetBlock(e.block,false)});
world.beforeEvents.explosion.subscribe(scheduleNativeBottleExplosion);
world.beforeEvents.explosion.subscribe(e=>{
 if(e.cancel)return;
 const grills=[],keep=[];for(const b of e.getImpactedBlocks()){if(b.typeId===GRILL_ID)grills.push({d:b.dimension,p:{...b.location}});else keep.push(b)}
 if(!grills.length)return;e.setImpactedBlocks(keep);
 system.run(()=>{for(const row of grills)try{customBreak(row.d.getBlock(row.p),undefined)}catch(error){console.warn('[Grilling explosion recovery] '+error)}});
});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.cancel)return;
 if(e.block.typeId===GRILL_ID){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>customBreak(dim.getBlock(loc),p));return}
 scheduleNativeBottleBreak(e);
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
function burnGrillContents(block,beforeState,nextState){
 const c=inv(block);if(!c)throw new Error('Grilling inventory unavailable');
 const output=new ItemStack('minecraft:charcoal',1+Math.floor(Math.random()*2));
 const steps=[0,1,2].map(i=>slotWrite(c,i,undefined));
 steps.push(acknowledgedDrop(block.dimension,output,{x:block.x+.5,y:block.y+.4,z:block.z+.5}));
 steps.push({apply:()=>writeState(block,nextState),rollback:()=>writeState(block,beforeState)});
 return commitStationTransfer(block,steps,'burn to charcoal').ok;
}
// Block ticks resume on chunk reload; no global registration cap or unload deletion.
function tickGrill(block){
 try{let state=readState(block),beforeState=state,before=state.phase;const result=tickState(state,occupied(block),1);state=result.state;if(result.events.some(x=>x.kind==='burn_to_charcoal')){burnGrillContents(block,beforeState,state);return}if(before!==state.phase)try{block.dimension.playSound('fire.fire',block.location)}catch{};writeTickState(block,beforeState,state);if(state.lit&&system.currentTick%4===0){const p={x:block.x+.5+(Math.random()-.5)*.45,y:block.y+.35,z:block.z+.5+(Math.random()-.5)*.45};if(Math.random()<.35)block.dimension.spawnParticle('minecraft:basic_smoke_particle',p);if(Math.random()<.12)block.dimension.spawnParticle('minecraft:basic_flame_particle',p)}}catch(error){if(system.currentTick%1200===0)console.warn('[Grilling tick] '+error)}
 finally{try{updateGrillAudio(block,readState(block).lit,occupied(block))}catch{try{removeGrillAudio(block)}catch{}}}
}
function tundraFactor(id){if(id==='minecraft:blue_ice')return 1.1055;if(['minecraft:ice','minecraft:packed_ice','minecraft:frosted_ice'].includes(id))return 1.11;return 1.3}
system.runInterval(()=>{
 for(const p of world.getAllPlayers()){try{
  const active=ACTIVE_EATS.get(p.id);
  if(active&&eatingStillCurrent(active.use,heldByHand(p,active.hand),p.selectedSlotIndex,now())){advanceBites(p,active);showJavaEatingHud(p,active,system.currentTick)} // Presentation never debits food.
  writeFx(p,readFx(p));const hunger=p.getComponent('minecraft:player.hunger'),sat=p.getComponent('minecraft:player.saturation');
  if(fxGet(p,'vigor')&&hunger&&sat){const prev=VIGOR_LAST.get(p.id);if(p.isSprinting&&prev){if(hunger.currentValue<prev.hunger)hunger.setCurrentValue(prev.hunger);if(sat.currentValue<prev.sat)sat.setCurrentValue(prev.sat)}VIGOR_LAST.set(p.id,{hunger:hunger.currentValue,sat:sat.currentValue})}else VIGOR_LAST.delete(p.id);
  const sneak=!!p.isSneaking,was=SNEAK_LAST.get(p.id)??false;if(sneak&&!was&&fxGet(p,'flatulence')){p.applyImpulse({x:0,y:.75,z:0});try{p.dimension.spawnParticle('minecraft:basic_smoke_particle',{x:p.location.x,y:p.location.y+.25,z:p.location.z});p.dimension.playSound('random.fizz',p.location)}catch{}}SNEAK_LAST.set(p.id,sneak);
  if(system.currentTick%5===0){if(fxGet(p,'mustard'))fleeCreepers(p);if(fxGet(p,'sulfur'))repelPhantoms(p)}
  if(fxGet(p,'tundra_strider')){try{const b=p.getBlockStandingOn();if(b&&TUNDRA_BLOCKS.has(b.typeId)){const v=p.getVelocity(),factor=tundraFactor(b.typeId);p.applyImpulse({x:v.x*(factor-1),y:0,z:v.z*(factor-1)});if(b.typeId==='minecraft:powder_snow'&&v.y<.02)p.applyImpulse({x:0,y:Math.min(.16,Math.max(.04,-v.y+.04)),z:0})}}catch{}}
  if(system.currentTick%20===0&&fxGet(p,'warmth')){const hp=p.getComponent('minecraft:health');if(hp&&hp.currentValue<hp.effectiveMax){if(nearHeat(p))hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+1));else if(p.dimension.id==='minecraft:nether'&&Math.random()<.25)hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+.5))}}
  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db){try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{};if(dragonPool(p)<=0&&p.getDynamicProperty(DRAGON_POOL_KEY)===undefined)setDragonPool(p,2)}else setDragonPool(p,undefined)}
  const numb=fxGet(p,'numb');if(numb&&!ACTIVE_EATS.has(p.id)){if(system.currentTick%12===0)try{p.playAnimation('animation.kg_a22.player.numb',{blendOutTime:.08})}catch{};NUMB_VISUAL.add(p.id)}else if(!numb&&NUMB_VISUAL.delete(p.id)){try{p.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}}
  if(system.currentTick%20===0){const m=heldMain(p),o=heldOff(p);if(m&&hotUntil(m)>0){refreshHotLore(m);setMain(p,m)}if(o&&hotUntil(o)>0){refreshHotLore(o);setOff(p,o)}}
 }catch{}}
},1);

world.afterEvents.playerLeave.subscribe(({playerId})=>{
 for(const cache of [ACTIVE_EATS,CUISINE_EATS,PLATE_EATS,SETTLED,VIGOR_LAST,SNEAK_LAST,THREAD_LAST])cache.delete(playerId);
 NUMB_VISUAL.delete(playerId);DRAGON_REPLAY.delete(playerId);DRAGON_PENDING.delete(playerId);
});

configureSecretVisuals(readEffectiveSkewerRows,restoreIngredient);
