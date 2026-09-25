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

const PRESS_PREFIX='kaleidoscope_grilling:a26_press_';
const VAT_PREFIX='kaleidoscope_grilling:a26_vat_';
const PRESS_REG='kaleidoscope_grilling:a26_press_registry';
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

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function key(prefix,block){return prefix+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function regKey(block){return block.dimension.id+'|'+block.x+'|'+block.y+'|'+block.z}
function readReg(){try{const x=JSON.parse(String(world.getDynamicProperty(PRESS_REG)??'[]'));return Array.isArray(x)?x:[]}catch{return []}}
function saveReg(rows){world.setDynamicProperty(PRESS_REG,JSON.stringify(rows.slice(0,256)))}
function registerPress(block){
 const rows=readReg(),k=regKey(block);if(rows.some(x=>x.k===k))return;
 rows.push({k,d:block.dimension.id,x:block.x,y:block.y,z:block.z});saveReg(rows);
}
function removePressReg(block){const k=regKey(block),rows=readReg().filter(x=>x.k!==k);saveReg(rows)}
function decHand(p,hand,count=1){
 if(creative(p))return true;const s=held(p,hand);if(!s||s.amount<count)return false;
 if(s.amount===count)setHand(p,hand,undefined);else{s.amount-=count;setHand(p,hand,s)}return true;
}
function give(p,stack){
 if(!stack)return;const c=playerContainer(p);if(!c){p.dimension.spawnItem(stack,p.location);return}
 try{const rem=c.addItem(stack);if(rem)p.dimension.spawnItem(rem,p.location)}catch{p.dimension.spawnItem(stack,p.location)}
}
function msg(p,text){try{p.onScreenDisplay.setActionBar(text)}catch{}}
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
 if(!block||block.typeId!==OIL_PRESS_ID)return;const state=normalizePress(s);
 world.setDynamicProperty(key(PRESS_PREFIX,block),JSON.stringify(state));syncPress(block,state);if(ensureRegistered)registerPress(block);
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
 if(!block||block.typeId!==BIG_VAT_ID)return;const state=normalizeVat(v);
 world.setDynamicProperty(key(VAT_PREFIX,block),JSON.stringify(state));syncVat(block,state);
}
function clearVat(block){world.setDynamicProperty(key(VAT_PREFIX,block))}

function vatPacked(stack){
 let type='',buckets=0;
 try{type=String(stack?.getDynamicProperty(VAT_ITEM_TYPE)??'');buckets=Number(stack?.getDynamicProperty(VAT_ITEM_BUCKETS)??0)|0}catch{}
 if(!type||buckets<=0)try{
  for(const line of stack?.getLore?.()??[]){const m=String(line).match(/^§7Fluid: ([a-z_]+) (\d+)\/8$/);if(m){type=m[1];buckets=Number(m[2]);break}}
 }catch{}
 return normalizeVat({type,buckets});
}
function vatItem(v){
 const state=normalizeVat(v);let out;try{out=new ItemStack(BIG_VAT_ID,1)}catch{return undefined}
 try{
  const lore=state.buckets?['§7Fluid: '+state.type+' '+state.buckets+'/'+VAT_CAPACITY_BUCKETS]:[];
  if(lore.length)out.setLore(lore);
  out.setDynamicProperty(VAT_ITEM_TYPE,state.type||undefined);out.setDynamicProperty(VAT_ITEM_BUCKETS,state.buckets||undefined);
 }catch{}
 return out;
}
function bucketType(id){return OIL_BUCKETS[id]??VANILLA_BUCKETS[id]??null}

function fillVatFromBucket(block,p,hand,item){
 const type=bucketType(item?.typeId);if(!type)return false;
 const v=readVat(block),next=vatInsert(v,type,1);
 if(!next.ok){msg(p,'§c大缸已滿或內容類型不符');return true}
 if(!creative(p))setHand(p,hand,new ItemStack('minecraft:bucket',1));writeVat(block,next.state);
 try{block.dimension.playSound(type==='lava'||type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',block.location,{volume:.9,pitch:.8+.5*next.state.buckets/VAT_CAPACITY_BUCKETS})}catch{}
 return true;
}
function takeVatBucket(block,p,hand){
 const v=readVat(block);if(!v.type||v.buckets<=0)return false;
 const id=TYPE_BUCKETS[v.type];if(!id)return false;
 const next=vatExtract(v,v.type,1);if(!next.ok)return false;
 if(!creative(p))setHand(p,hand,new ItemStack(id,1));else give(p,new ItemStack(id,1));
 writeVat(block,next.state);return true;
}
function fillPotFromVat(block,p,hand,item){
 const v=readVat(block);if(!['canola','secret_chili','premium_chili'].includes(v.type))return false;
 const oil=readCookeryOilPot(item),type=item.typeId===COOKERY_FILLED?oil.type:'',count=item.typeId===COOKERY_FILLED?oil.count:0;
 const plan=potFillPlan(v,type,count);if(!plan.ok){msg(p,'§c大缸已滿、油壺已滿或油種不同');return true}
 const next=vatExtract(v,v.type,plan.buckets);if(!next.ok)return true;
 const pot=buildCookeryOilPot(plan.type,plan.nextCount,item);if(pot)setHand(p,hand,pot);writeVat(block,next.state);return true;
}
function vatStatus(block,p){const v=readVat(block);msg(p,'§7大缸：'+(v.type||'empty')+' '+v.buckets+'/'+VAT_CAPACITY_BUCKETS+' 桶')}

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
 let sent=false;try{for(const p of block.dimension.getPlayers({location:block.location,maxDistance:6})){msg(p,text);sent=true}}catch{}
 if(!sent&&source)msg(source,text);
}
function residueEject(block,count){
 if(count<=0)return;let facing='north';try{facing=String(block.permutation.getState('minecraft:cardinal_direction')??'north')}catch{}
 const o=faceOffset(facing)??{x:0,y:0,z:-1},loc={x:block.x+.5+o.x*.72,y:block.y+.58,z:block.z+.5+o.z*.72};
 try{block.dimension.spawnItem(new ItemStack(OIL_RESIDUE_ID,count),loc)}catch{}
}
function finishPress(block,source){
 const state=readPress(block),probe=scanVat(block);
 if(probe.status==='SUCCESS'&&probe.block){
  const v=readVat(probe.block),ins=vatInsert(v,'canola',PRESS_OUTPUT_BUCKETS);
  if(!ins.ok){const fail=finishPressTransfer(state,'FULL');writePress(block,fail.state);broadcastPressFailure(block,'FULL',source);return false}
  writeVat(probe.block,ins.state);
  const done=finishPressTransfer(state,'SUCCESS');writePress(block,done.state);residueEject(block,done.residue);
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
 const dim=block.dimension,loc={...block.location},pid=p.id;
 system.runTimeout(()=>{
  const b=dim.getBlock(loc);if(!b||b.typeId!==OIL_PRESS_ID)return;const current=readPress(b),hit=impactPress(current,amount);if(!hit.ok)return;
  writePress(b,hit.state);
  try{dim.playSound('random.anvil_land',b.location,{volume:1.15,pitch:.88})}catch{}
  try{for(let i=0;i<6;i++)dim.spawnParticle('minecraft:critical_hit_emitter',{x:b.x+.5+(Math.random()-.5)*.4,y:b.y+.9+(Math.random()-.5)*.2,z:b.z+.5+(Math.random()-.5)*.4})}catch{}
  try{const source=world.getEntity(pid);if(source)msg(source,'§7榨油進度 '+hit.state.progress+'/'+PRESS_REQUIRED_PROGRESS)}catch{}
 },PRESS_IMPACT_TICK);
 return true;
}
function interactPress(block,p,item,hand=null){
 const state=readPress(block);
 if(state.waiting){finishPress(block,p);return}
 const actualHand=hand??(item?handFor(p,item.typeId):null);
 if(item?.typeId===OIL_CAKE_ID){
  const x=pressAddCake(state);if(!x.ok){msg(p,'§e榨油器最多放 4 個油餅');return}
  if(actualHand&&!decHand(p,actualHand,1))return;writePress(block,x.state);
  try{block.dimension.playSound('dig.grass',block.location,{volume:.8,pitch:1})}catch{};return;
 }
 const amount=toolProgress(item?.typeId);if(amount>0){startPress(block,p,amount);return}
 msg(p,'§7榨油器：油餅 '+state.cakes+'/4，進度 '+state.progress+'/'+PRESS_REQUIRED_PROGRESS);
}
function breakPress(block,p){
 const s=readPress(block),dim=block.dimension,loc={x:block.x+.5,y:block.y+.5,z:block.z+.5};clearPress(block);block.setType('minecraft:air');
 if(creative(p))return;try{dim.spawnItem(new ItemStack(OIL_PRESS_ID,1),loc)}catch{};if(s.cakes)try{dim.spawnItem(new ItemStack(OIL_CAKE_ID,s.cakes),loc)}catch{}
}
function breakVat(block,p){
 const v=readVat(block),dim=block.dimension,loc={x:block.x+.5,y:block.y+.5,z:block.z+.5};clearVat(block);block.setType('minecraft:air');
 if(creative(p))return;const item=vatItem(v);if(item)dim.spawnItem(item,loc);
}
function placePackedVat(support,face,p,item,hand=null){
 const target=targetFor(support,face);if(!replaceable(target))return false;const actualHand=hand??handFor(p,item?.typeId);if(!actualHand)return false;
 const packed=vatPacked(item);target.setType(BIG_VAT_ID);writeVat(target,packed);decHand(p,actualHand,1);return true;
}
function interactVat(block,p,item,hand=null){
 const actualHand=hand??(item?handFor(p,item.typeId):null);if(!item){vatStatus(block,p);return}
 if((item.typeId===COOKERY_EMPTY||item.typeId===COOKERY_FILLED)&&actualHand&&fillPotFromVat(block,p,actualHand,item))return;
 if(bucketType(item.typeId)&&actualHand&&fillVatFromBucket(block,p,actualHand,item))return;
 if(item.typeId==='minecraft:bucket'&&actualHand&&takeVatBucket(block,p,actualHand))return;
 vatStatus(block,p);
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
 const rows=readReg(),keep=[];
 for(const row of rows){
  let dim,b;try{dim=world.getDimension(row.d);b=dim.getBlock({x:row.x,y:row.y,z:row.z})}catch{continue}
  if(!b||b.typeId!==OIL_PRESS_ID)continue;keep.push(row);const s=readPress(b);
  if(s.completionDelay>0){
   const next={...s,completionDelay:s.completionDelay-1};writePress(b,next,false);
   if(next.completionDelay===0&&next.progress>=PRESS_REQUIRED_PROGRESS)finishPress(b);
  }
 }
 if(keep.length!==rows.length)saveReg(keep);
},1);

export function a26ReadPress(block){return readPress(block)}
export function a26ProbePressContainer(block){return scanVat(block)}
export function a26ReadVat(block){return readVat(block)}
export function a26VatItem(v){return vatItem(v)}
