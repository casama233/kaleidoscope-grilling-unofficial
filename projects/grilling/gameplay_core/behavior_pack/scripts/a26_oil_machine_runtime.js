import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,setItemLore} from './itemData.js';
import {interactionFeedback} from './a283_interaction_feedback.js';
import {world,system,ItemStack} from '@minecraft/server';
import {
 PRESS_MAX_CAKES,PRESS_REQUIRED_PROGRESS,PRESS_COOLDOWN_TICKS,PRESS_IMPACT_TICK,PRESS_COMPLETION_DELAY,
 PRESS_OUTPUT_BUCKETS,VAT_CAPACITY_BUCKETS,OIL_POT_CAPACITY,OIL_BUCKET_POINTS,
 OIL_CAKE_ID,OIL_RESIDUE_ID,OIL_PRESS_ID,BIG_VAT_ID,
 toolProgress,pressVisualStage,normalizePress,pressAddCake,impactPress,finishPressTransfer,
 normalizeVat,vatVisualLevel,vatInsert,vatExtract,potFillPlan,nearbyOffsets
} from './a26_oil_machine_core.js';
import {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,readCookeryOilPot,buildCookeryOilPot} from './a2734_cookery_oil_pot_adapter.js';
import {playerInventory as playerContainer,getMainHand as main,getOffHand as off,setMainHand as setMain,setOffHand as setOff,findHand as handFor,getHand as held,setHand,isCreative as creative} from './a2735_player_io.js';
import {isInitialBlockPress} from './a275_grill_input_core.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './a2762_interaction_intent_adapter.js';
import {captureWritableHand} from './a2735_player_io.js';
import {commitSteps} from './a277_grill_transaction_core.js';
import {createOilPressRegistry} from './oil_press_registry.js';
import {ensureOilHandPublished} from './oil_api_client.js';

const PRESS_PREFIX='kaleidoscope_grilling:a26_press_';
const VAT_PREFIX='kaleidoscope_grilling:a26_vat_';
const PRESS_REG='kaleidoscope_grilling:a26_press_registry';
const pressRegistry=createOilPressRegistry(world,PRESS_REG);
const VAT_ITEM_TYPE='kaleidoscope_grilling:vat_type';
const VAT_ITEM_BUCKETS='kaleidoscope_grilling:vat_buckets';
const OIL_BUCKETS=Object.freeze({
 'kaleidoscope_grilling:canola_oil_bucket':'canola',
 'kaleidoscope_grilling:secret_chili_oil_bucket':'secret_chili',
 'kaleidoscope_grilling:premium_chili_oil_bucket':'premium_chili'
});
const TYPE_BUCKETS=Object.freeze({
 canola:'kaleidoscope_grilling:canola_oil_bucket',
 secret_chili:'kaleidoscope_grilling:secret_chili_oil_bucket',
 premium_chili:'kaleidoscope_grilling:premium_chili_oil_bucket',
 water:'minecraft:water_bucket',
 lava:'minecraft:lava_bucket'
});
const VANILLA_BUCKETS=Object.freeze({'minecraft:water_bucket':'water','minecraft:lava_bucket':'lava'});
const PRESS_COOLDOWNS=new Map();
const TRANSACTION_FAULTS=new Set(),FAULT_PREFIX='kaleidoscope_grilling:oil_transaction_fault_';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function key(prefix,block){return prefix+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function registryRow(block){return {d:block.dimension.id,x:block.x,y:block.y,z:block.z}}
function registerPress(block){
 pressRegistry.add(registryRow(block));
}
function removePressReg(block){pressRegistry.remove(registryRow(block))}
function decHand(p,hand,count=1){
 if(creative(p))return true;const s=held(p,hand);if(!s||s.amount<count)return false;
 if(s.amount===count)setHand(p,hand,undefined);else{s.amount-=count;setHand(p,hand,s)}return true;
}
const msg=interactionFeedback;
function faceName(face){return String(face??'').toLowerCase()}
function faceOffset(face){
 switch(faceName(face)){case'north':return{x:0,y:0,z:-1};case'south':return{x:0,y:0,z:1};case'west':return{x:-1,y:0,z:0};case'east':return{x:1,y:0,z:0};case'up':return{x:0,y:1,z:0};case'down':return{x:0,y:-1,z:0};default:return null}
}
function targetFor(block,face){const o=faceOffset(face);return o?block.dimension.getBlock({x:block.x+o.x,y:block.y+o.y,z:block.z+o.z}):undefined}
function replaceable(b){return !!b&&['minecraft:air','minecraft:short_grass','minecraft:tall_grass','minecraft:snow_layer'].includes(b.typeId)}

function readPress(block){
 try{const raw=world.getDynamicProperty(key(PRESS_PREFIX,block));return normalizePress(typeof raw==='string'?JSON.parse(raw):{})}catch{return normalizePress({})}
}
function syncPress(block,s){
 const state=normalizePress(s);
 try{
  let p=block.permutation.withState('kaleidoscope_grilling:cake_count',state.cakes);
  p=p.withState('kaleidoscope_grilling:press_stage',pressVisualStage(state.progress));block.setPermutation(p);
 }catch{}
}
function writePress(block,s,ensureRegistered=true){
 if(!block||block.typeId!==OIL_PRESS_ID)throw Error('Oil press replaced or unavailable');const state=normalizePress(s);
 const pending=state.completionDelay>0||state.progress>=PRESS_REQUIRED_PROGRESS;
 if(ensureRegistered&&pending)registerPress(block);
 world.setDynamicProperty(key(PRESS_PREFIX,block),JSON.stringify(state));syncPress(block,state);
 if(!pending)removePressReg(block);
}
function clearPress(block){world.setDynamicProperty(key(PRESS_PREFIX,block));removePressReg(block)}

function readVat(block){
 try{const raw=world.getDynamicProperty(key(VAT_PREFIX,block));return normalizeVat(typeof raw==='string'?JSON.parse(raw):{})}catch{return normalizeVat({})}
}
function syncVat(block,v){
 const state=normalizeVat(v);
 try{
  let p=block.permutation.withState('kaleidoscope_grilling:vat_level',vatVisualLevel(state.buckets));
  p=p.withState('kaleidoscope_grilling:vat_fluid',state.type||'empty');block.setPermutation(p);
 }catch{}
}
function writeVat(block,v){
 if(!block||block.typeId!==BIG_VAT_ID)throw Error('Oil vat replaced or unavailable');const state=normalizeVat(v);
 world.setDynamicProperty(key(VAT_PREFIX,block),JSON.stringify(state));syncVat(block,state);
}
function clearVat(block){world.setDynamicProperty(key(VAT_PREFIX,block))}

function vatPacked(stack){
 let type='',buckets=0;
 try{type=String(getItemProperty(stack,VAT_ITEM_TYPE)??'');buckets=Number(getItemProperty(stack,VAT_ITEM_BUCKETS)??0)|0}catch{}
 if(!type||buckets<=0)try{
  for(const line of getItemLore(stack)??[]){const m=String(line).match(/^§7Fluid: ([a-z_]+) (\d+)\/8$/);if(m){type=m[1];buckets=Number(m[2]);break}}
 }catch{}
 return normalizeVat({type,buckets});
}
function vatItem(v){
 const state=normalizeVat(v);let out;try{out=new ItemStack(BIG_VAT_ID,1)}catch{return undefined}
 try{
  const lore=state.buckets?['§7Fluid: '+state.type+' '+state.buckets+'/'+VAT_CAPACITY_BUCKETS]:[];
  if(lore.length)setItemLore(out,lore);
  setItemProperty(out,VAT_ITEM_TYPE,state.type||undefined);setItemProperty(out,VAT_ITEM_BUCKETS,state.buckets||undefined);
 }catch{}
 return out;
}
function bucketType(id){return OIL_BUCKETS[id]??VANILLA_BUCKETS[id]??null}

function assertOilMachineSafe(block){
 const id=key(FAULT_PREFIX,block);
 if(TRANSACTION_FAULTS.has(id)||world.getDynamicProperty(id)!==undefined)throw Error('Oil machine requires recovery after an incomplete rollback');
}
function oilTransaction(steps,blocks){
 for(const block of blocks)assertOilMachineSafe(block);
 const result=commitSteps(steps);
 if(result.rollbackErrors)for(const block of blocks){
  const id=key(FAULT_PREFIX,block);TRANSACTION_FAULTS.add(id);
  try{world.setDynamicProperty(id,'incomplete rollback; inspect before recovery')}catch(error){console.warn('[Grilling oil recovery marker failed] '+error);}
 }
 if(!result.ok)throw Error('Oil transaction failed; rollback failures='+result.rollbackErrors);
}
// One filled bucket: reserve an exact inventory slot, or retain the spawned
// entity for rollback. Never overwrite the rest of a stack of empty buckets.
function bucketDelivery(p,hand,output){
 const container=playerContainer(p);if(!container)throw Error('Oil bucket inventory unavailable');
 let slot=-1,before,after,drop;
 for(let i=0;i<container.size;i++){
  if(hand==='main'&&i===p.selectedSlotIndex)continue;
  const item=container.getItem(i);
  if(!item||(item.isStackableWith(output)&&item.amount<item.maxAmount)){
   slot=i;before=item?.clone();after=item?.clone()??output;
   if(item)after.amount++;break;
  }
 }
 return {apply(){if(slot>=0)container.setItem(slot,after);else{drop=p.dimension.spawnItem(output,{...p.location,y:p.location.y+.5});if(!drop)throw Error('Oil bucket drop unavailable')}},
  rollback(){if(slot>=0)container.setItem(slot,before);else if(drop)drop.remove()}};
}

function fillVatFromBucket(block,p,hand,item){
 const type=bucketType(item?.typeId);if(!type)return false;
 const v=readVat(block),next=vatInsert(v,type,1);
 if(!next.ok){msg(p,'§c大缸已滿或內容類型不符');return true}
 const storage=captureWritableHand(p,hand),free=creative(p);
 oilTransaction([
  {apply(){if(!free)storage.write(new ItemStack('minecraft:bucket',1))},rollback(){if(!free)storage.write(storage.before)}},
  {apply(){writeVat(block,next.state)},rollback(){writeVat(block,v)}}
 ],[block]);
 try{block.dimension.playSound(type==='lava'||type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',block.location,{volume:.9,pitch:.8+.5*next.state.buckets/VAT_CAPACITY_BUCKETS})}catch{}
 return true;
}
function takeVatBucket(block,p,hand){
 const v=readVat(block);if(!v.type||v.buckets<=0)return false;
 const id=TYPE_BUCKETS[v.type];if(!id)return false;
 const next=vatExtract(v,v.type,1);if(!next.ok)return false;
 const storage=captureWritableHand(p,hand),before=storage.before;
 if(before?.typeId!=='minecraft:bucket'||before.amount<1)return false;
 const steps=[];
 // NeoForge FluidUtil: creative drains the tank but keeps its input and gives
 // no filled bucket. Survival single replaces; a stack stows/drops the result.
 if(!creative(p)){
  const output=new ItemStack(id,1),after=before.amount===1?output:before.clone();
  if(before.amount>1)after.amount--;
  steps.push({apply(){storage.write(after)},rollback(){storage.write(before)}});
  if(before.amount>1)steps.push(bucketDelivery(p,hand,output));
 }
 steps.push({apply(){writeVat(block,next.state)},rollback(){writeVat(block,v)}});
 oilTransaction(steps,[block]);return true;
}
function fillPotFromVat(block,p,hand,item){
 if(block?.typeId!=='kaleidoscope_grilling:big_vat')return true;
 if(!ensureOilHandPublished(p,hand,()=>fillPotFromVat(block,p,hand,held(p,hand))))return true;
 item=held(p,hand);
 const v=readVat(block);if(!['canola','secret_chili','premium_chili'].includes(v.type))return false;
 const oil=readCookeryOilPot(item),type=item.typeId===COOKERY_FILLED?oil.type:'',count=item.typeId===COOKERY_FILLED?oil.count:0;
 const plan=potFillPlan(v,type,count);if(!plan.ok){msg(p,'§c大缸已滿、油壺已滿或油種不同');return true}
 const next=vatExtract(v,v.type,plan.buckets);if(!next.ok)return true;
 const pot=buildCookeryOilPot(plan.type,plan.nextCount,item);if(!pot)return true;
 const storage=captureWritableHand(p,hand);
 oilTransaction([
  {apply(){storage.write(pot)},rollback(){storage.write(storage.before)}},
  {apply(){writeVat(block,next.state)},rollback(){writeVat(block,v)}}
 ],[block]);return true;
}

function scanVat(press){
 let fallback={status:'NO_CONTAINER',block:null};
 for(const o of nearbyOffsets()){
  let b;try{b=press.dimension.getBlock({x:press.x+o.x,y:press.y+o.y,z:press.z+o.z})}catch{continue}
  if(!b||b.typeId!==BIG_VAT_ID)continue;const v=readVat(b);
  if(v.buckets>0&&v.type!=='canola'){
   if(fallback.status==='NO_CONTAINER')fallback={status:'INCOMPATIBLE',block:b};continue;
  }
  if(v.buckets+PRESS_OUTPUT_BUCKETS>VAT_CAPACITY_BUCKETS){fallback={status:'FULL',block:b};continue}
  return {status:'SUCCESS',block:b};
 }
 return fallback;
}
function broadcastPressFailure(block,status,source){
 const text=status==='FULL'?'§c附近大缸容量不足':status==='INCOMPATIBLE'?'§c附近大缸裝有不同流體':'§c附近沒有可接 4 桶菜籽油的大缸';
 if(source)msg(source,text);
}
function residueEject(block,count){
 if(count<=0)return;let facing='north';try{facing=String(block.permutation.getState('minecraft:cardinal_direction')??'north')}catch{}
 const o=faceOffset(facing)??{x:0,y:0,z:-1},loc={x:block.x+.5+o.x*.72,y:block.y+.58,z:block.z+.5+o.z*.72};
 const entity=block.dimension.spawnItem(new ItemStack(OIL_RESIDUE_ID,count),loc);
 if(!entity)throw Error('Oil residue drop unavailable');return entity;
}
function finishPress(block,source){
 assertOilMachineSafe(block);
 const state=readPress(block),probe=scanVat(block);
 if(probe.status==='SUCCESS'&&probe.block){
  const v=readVat(probe.block),ins=vatInsert(v,'canola',PRESS_OUTPUT_BUCKETS);
  if(!ins.ok){const fail=finishPressTransfer(state,'FULL');writePress(block,fail.state);broadcastPressFailure(block,'FULL',source);return false}
  const done=finishPressTransfer(state,'SUCCESS');let residue;
  oilTransaction([
   {apply(){writeVat(probe.block,ins.state)},rollback(){writeVat(probe.block,v)}},
   {apply(){writePress(block,done.state)},rollback(){writePress(block,state)}},
   {apply(){residue=residueEject(block,done.residue)},rollback(){if(residue)residue.remove()}}
  ],[block,probe.block]);
  try{block.dimension.playSound('piston.in',block.location,{volume:.8,pitch:.9})}catch{};return true;
 }
 const fail=finishPressTransfer(state,probe.status);writePress(block,fail.state);broadcastPressFailure(block,probe.status,source);return false;
}
function startPress(block,p,amount){
 const state=readPress(block);
 if(state.cakes<PRESS_MAX_CAKES){msg(p,'§e榨油器需要先放滿 4 個油餅（'+state.cakes+'/4）');return true}
 if(state.waiting){finishPress(block,p);return true}
 const cd=key(PRESS_PREFIX,block)+'|'+p.id,now=system.currentTick;
 if(now<(PRESS_COOLDOWNS.get(cd)??-1))return true;
 const dry=impactPress(state,amount);if(!dry.ok)return true;
 PRESS_COOLDOWNS.set(cd,now+PRESS_COOLDOWN_TICKS);
 try{p.playAnimation('animation.kg_a26.player.anvil_press',{blendOutTime:.05})}catch{}
 const dim=block.dimension,loc={...block.location};
 system.runTimeout(()=>{
  const b=dim.getBlock(loc);if(!b||b.typeId!==OIL_PRESS_ID)return;const current=readPress(b),hit=impactPress(current,amount);if(!hit.ok)return;
  writePress(b,hit.state);
  try{dim.playSound('random.anvil_land',b.location,{volume:1.15,pitch:.88})}catch{}
  try{for(let i=0;i<6;i++)dim.spawnParticle('minecraft:critical_hit_emitter',{x:b.x+.5+(Math.random()-.5)*.4,y:b.y+.9+(Math.random()-.5)*.2,z:b.z+.5+(Math.random()-.5)*.4})}catch{}
 },PRESS_IMPACT_TICK);
 return true;
}
function interactPress(block,p,item,hand=null){
 assertOilMachineSafe(block);
 const state=readPress(block);
 if(state.waiting||state.progress>=PRESS_REQUIRED_PROGRESS){finishPress(block,p);return}
 const actualHand=hand??(item?handFor(p,item.typeId):null);
 if(item?.typeId===OIL_CAKE_ID){
  const x=pressAddCake(state);if(!x.ok){msg(p,'§e榨油器最多放 4 個油餅');return}
  if(actualHand&&!decHand(p,actualHand,1))return;writePress(block,x.state);
  try{block.dimension.playSound('dig.grass',block.location,{volume:.8,pitch:1})}catch{};return;
 }
 const amount=toolProgress(item?.typeId,item?.getTags?.()??[]);if(amount>0){startPress(block,p,amount);return}

}
function breakPress(block,p){
 assertOilMachineSafe(block);
 const s=readPress(block),dim=block.dimension,loc={x:block.x+.5,y:block.y+.5,z:block.z+.5};clearPress(block);block.setType('minecraft:air');
 if(creative(p))return;try{dim.spawnItem(new ItemStack(OIL_PRESS_ID,1),loc)}catch{};if(s.cakes)try{dim.spawnItem(new ItemStack(OIL_CAKE_ID,s.cakes),loc)}catch{}
}
function breakVat(block,p){
 assertOilMachineSafe(block);
 const v=readVat(block),dim=block.dimension,loc={x:block.x+.5,y:block.y+.5,z:block.z+.5};clearVat(block);block.setType('minecraft:air');
 if(creative(p))return;const item=vatItem(v);if(item)dim.spawnItem(item,loc);
}
function placePackedVat(support,face,p,item,hand=null){
 const target=targetFor(support,face);if(!replaceable(target))return false;const actualHand=hand??handFor(p,item?.typeId);if(!actualHand)return false;
 const packed=vatPacked(item);target.setType(BIG_VAT_ID);writeVat(target,packed);decHand(p,actualHand,1);return true;
}
function interactVat(block,p,item,hand=null){
 assertOilMachineSafe(block);
 const actualHand=hand??(item?handFor(p,item.typeId):null);if(!item){return}
 if((item.typeId===COOKERY_EMPTY||item.typeId===COOKERY_FILLED)&&actualHand&&fillPotFromVat(block,p,actualHand,item))return;
 if(bucketType(item.typeId)&&actualHand&&fillVatFromBucket(block,p,actualHand,item))return;
 if(item.typeId==='minecraft:bucket'&&actualHand&&takeVatBucket(block,p,actualHand))return;

}

function doubleCropGrowth(block,p,hand){
 let states;try{states=block.permutation.getAllStates()}catch{return false}
 const keyName=['growth','minecraft:growth','age','minecraft:age'].find(k=>typeof states[k]==='number');if(!keyName)return false;
 const current=Number(states[keyName]);let max=current;
 for(let v=current+1;v<=15;v++)try{block.permutation.withState(keyName,v);max=v}catch{break}
 if(max<=current)return false;
 let next=current;
 for(let pass=0;pass<2;pass++)next=Math.min(max,next+2+Math.floor(Math.random()*4));
 try{block.setPermutation(block.permutation.withState(keyName,next))}catch{return false}
 if(!creative(p))decHand(p,hand,1);
 try{block.dimension.spawnParticle('minecraft:crop_growth_emitter',{x:block.x+.5,y:block.y+.5,z:block.z+.5})}catch{}
 return true;
}

world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 try{
  const b=e.block,p=e.player,intent=captureInteractionIntent(p,e.itemStack),hand=intent.hand,item=held(p,hand),first=isInitialBlockPress(e.isFirstEvent);
  const defer=fn=>system.run(()=>{if(!interactionIntentStillCurrent(p,intent)){msg(p,'§7操作已取消：互動後手持物品已改變');return}fn()});
  if(b.typeId===OIL_PRESS_ID){e.cancel=true;if(!first)return;const dim=b.dimension,loc={...b.location};defer(()=>interactPress(dim.getBlock(loc),p,held(p,hand),hand));return}
  if(b.typeId===BIG_VAT_ID){e.cancel=true;if(!first)return;const dim=b.dimension,loc={...b.location};defer(()=>interactVat(dim.getBlock(loc),p,held(p,hand),hand));return}
  if(item?.typeId===BIG_VAT_ID){
   const target=targetFor(b,e.blockFace);if(replaceable(target)){e.cancel=true;if(!first)return;const dim=b.dimension,loc={...b.location},face=e.blockFace;defer(()=>{const current=held(p,hand);if(current?.typeId===BIG_VAT_ID)placePackedVat(dim.getBlock(loc),face,p,current,hand)});return}
  }
  if(item?.typeId===OIL_RESIDUE_ID){
   let can=false;try{const states=b.permutation.getAllStates();can=['growth','minecraft:growth','age','minecraft:age'].some(k=>typeof states[k]==='number')}catch{}
   if(can){e.cancel=true;if(!first)return;const dim=b.dimension,loc={...b.location};defer(()=>doubleCropGrowth(dim.getBlock(loc),p,hand));return}
  }
 }catch{}
});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 try{
  if(e.block.typeId===OIL_PRESS_ID){e.cancel=true;const p=e.player,dim=e.block.dimension,loc={...e.block.location};system.run(()=>breakPress(dim.getBlock(loc),p));return}
  if(e.block.typeId===BIG_VAT_ID){e.cancel=true;const p=e.player,dim=e.block.dimension,loc={...e.block.location};system.run(()=>breakVat(dim.getBlock(loc),p));return}
 }catch{}
});

system.runInterval(()=>{
 let rows;try{rows=pressRegistry.rows()}catch(error){console.warn('[Grilling oil registry] '+error);return;}
 for(const row of rows){
  let dim,b;try{dim=world.getDimension(row.d);b=dim.getBlock({x:row.x,y:row.y,z:row.z})}catch{continue}
  // Missing block/chunk is unknown, not proof that the machine was removed.
  if(!b)continue;
  try{
   if(b.typeId!==OIL_PRESS_ID){pressRegistry.remove(row);continue;}
   const faultId=key(FAULT_PREFIX,b);
   if(TRANSACTION_FAULTS.has(faultId)||world.getDynamicProperty(faultId)!==undefined){pressRegistry.remove(row);continue;}
   const s=readPress(b);
   if(s.completionDelay>0){
    const next={...s,completionDelay:s.completionDelay-1};writePress(b,next,false);
    if(next.completionDelay===0&&next.progress>=PRESS_REQUIRED_PROGRESS)finishPress(b);
   }else if(s.progress>=PRESS_REQUIRED_PROGRESS&&!s.waiting)finishPress(b);
   else pressRegistry.remove(row);
  }catch(error){console.warn('[Grilling oil press] '+error);}
 }
},1);

export function a26ReadPress(block){return readPress(block)}
export function a26ProbePressContainer(block){return scanVat(block)}
export function a26ReadVat(block){return readVat(block)}
export function a26VatItem(v){return vatItem(v)}
