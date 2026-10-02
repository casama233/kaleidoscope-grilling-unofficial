/** Fault-injected production functions; storage doubles are not Minecraft players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as tx from '../../projects/grilling/gameplay_core/behavior_pack/scripts/plate_transaction_core.js';
import * as plate from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_core.js';
import * as snapshot from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
import * as item from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
const base=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const source=fs.readFileSync(new URL('a25_plate_recipe_runtime.js',base),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const))/g,'');
class Stack{
 constructor(typeId,amount=1){Object.assign(this,{typeId,amount,maxAmount:1,props:{},lore:[],keepOnDeath:false,lockMode:'none'});}
 clone(){const s=new Stack(this.typeId,this.amount);Object.assign(s,structuredClone({...this}));return s;}
 getDynamicProperty(k){return this.props[k]} getDynamicPropertyIds(){return Object.keys(this.props)}
 setDynamicProperty(k,v){if(v===undefined)delete this.props[k];else this.props[k]=v}
 getRawLore(){return structuredClone(this.lore)} getLore(){return this.lore.map(x=>typeof x==='string'?x:x.text??'')}
 setLore(v){this.lore=structuredClone(v)}
 getCanDestroy(){return []}getCanPlaceOn(){return []}setCanDestroy(){}setCanPlaceOn(){}
 getComponent(k){return k==='minecraft:food'?{nutrition:4,saturationModifier:.4}:undefined}
}
const N='kaleidoscope_grilling:',PLATE=N+'skewer_plate_block',food=()=>{const s=new Stack(N+'grilled_beef_skewer');s.nameTag='named food';s.lore=[{translate:'item.foreign.food',with:['保留']}];s.props['foreign:value']='preserve';return s;};
function fixture(){
 const dp=new Map(),slots=new Map(),entities=[],events={};let fault;
 function write(k,v){if(v===undefined)dp.delete(k);else dp.set(k,v);if(fault?.(k,v))throw Error('post-write failure')}
 const permutation=(typeId,states={})=>({type:{id:typeId},getState:k=>states[k],getAllStates:()=>({...states}),withState(k,v){return permutation(typeId,{...states,[k]:v})}});
 const dimension={id:'minecraft:overworld',getBlock:()=>block,playSound(){},spawnItem(stack){
  const e={isValid:true,stack:stack.clone(),getComponent(){return {itemStack:fault?.('dropRead')?new Stack('minecraft:stone'):this.stack}},remove(){if(fault?.('dropRemoveBefore'))throw Error('drop removal unavailable');this.isValid=false;if(fault?.('dropRemove'))throw Error('drop cleanup post-write failure')}};
  entities.push(e);if(fault?.('spawn'))throw Error('spawn outcome unknown');return e;
 }};
 const block={x:0,y:80,z:0,location:{x:0,y:80,z:0},dimension,typeId:PLATE,permutation:permutation(PLATE,{[N+'plate_count']:0,'minecraft:cardinal_direction':'north'}),
  setPermutation(p){this.permutation=p;this.typeId=p.type.id;if(fault?.('block',p))throw Error('block post-write failure')},
  setType(id){this.typeId=id;this.permutation=permutation(id,id===PLATE?{[N+'plate_count']:0,'minecraft:cardinal_direction':'north'}:{});if(id==='minecraft:air'&&fault?.('remove'))throw Error('remove post-write failure')}};
 const holder={selectedSlotIndex:0,isSneaking:true,getRotation:()=>({y:90}),creative:false};
 const held=(p,h)=>slots.get(h==='off'?'off':p.selectedSlotIndex);
 const setHand=(p,h,s)=>{const key=h==='off'?'off':p.selectedSlotIndex;slots.set(key,s?.clone());if(fault?.('hand',s))throw Error('hand post-write failure')};
 const captureWritableHand=(p,h)=>{const key=h==='off'?'off':p.selectedSlotIndex;return {before:slots.get(key)?.clone(),read:()=>slots.get(key),write(s){slots.set(key,s?.clone());if(fault?.('hand',s))throw Error('hand post-write failure')}}};
 const c=vm.createContext({...tx,...plate,...snapshot,...item,recipeTable:()=>[{id:N+'raw_beef_skewer',cooked:N+'grilled_beef_skewer'}],RAW_SKEWER_TAG:'raw',GRILLED_SKEWER_TAG:'grilled',ItemStack:Stack,
  world:{getDynamicProperty:k=>dp.get(k),setDynamicProperty:write,beforeEvents:{itemUse:{subscribe(){}},playerInteractWithBlock:{subscribe(){}},playerBreakBlock:{subscribe(){}},explosion:{subscribe(fn){events.explosion=fn}}},afterEvents:{playerBreakBlock:{subscribe(){}}}},
  system:{run(){}},console:{warn(){}},SECRET_ID:N+'secret_skewer',captureWritableHand,
  heldByHand:held,setHand,creative:p=>p?.creative??false,hasSolidTop:()=>true,
  interactionStackSignature:s=>s?JSON.stringify(s):'',interactionFeedback(){},UNFINISHED_ID:N+'unfinished_skewer'});
 vm.runInContext(source+'\nglobalThis.api={readPlateBlock,placePlateOn,handlePlateBlock,plateStorageStep,plateTransaction,posKey,plateFaultKey,breakPlate};',c);
 const api=c.api,key=api.posKey(N+'a25_plate_',block);
 return {dp,slots,entities,events,block,holder,api,key,set fault(f){fault=f},oneFailure(target){let once=true;fault=k=>k===target&&once?(once=false,true):false},rows(n=1){const rows=Array.from({length:n},()=>({id:food().typeId,native:snapshot.captureSkewerMetadata(food()),nutrition:4,saturation:.4}));dp.set(key,JSON.stringify(rows));block.permutation=block.permutation.withState(N+'plate_count',n);return rows;}};
}
test('invalid saved rows are rejected, never filtered or truncated',()=>{
 for(const raw of [null,1,'{',JSON.stringify({}),JSON.stringify([null]),JSON.stringify([{id:'bad'}]),JSON.stringify([{id:'x:food',native:{version:2,id:'x:food'}}]),JSON.stringify([{id:'x:food',native:{version:1,id:'x:other'}}]),JSON.stringify(Array(6).fill({id:'x:food'}))])assert.throws(()=>tx.decodePlateStorage(raw));
 assert.deepEqual(tx.decodePlateStorage(undefined),[]);
 const f=fixture();f.dp.set(f.key,'damaged');assert.throws(()=>f.api.readPlateBlock(f.block));assert.equal(f.dp.get(f.key),'damaged');
});
test('placement uses Java player direction, including wrap and exact quarter-turn boundaries',()=>{
 for(const [yaw,expected] of [[0,'south'],[90,'west'],[180,'north'],[-90,'east'],[360,'south'],[45,'west'],[-45,'south'],[-135,'east']])assert.equal(tx.plateFacingFromYaw(yaw),expected);
 assert.throws(()=>tx.plateFacingFromYaw(NaN));
});
for(const hand of ['main','off']){
 test('taking last skewer in '+hand+' preserves native metadata',()=>{
  const f=fixture(),rows=f.rows(2);f.api.handlePlateBlock(f.block,f.holder,hand);
  assert.equal(JSON.parse(f.dp.get(f.key)).length,1);assert.equal(f.block.permutation.getState(N+'plate_count'),1);
  assert.deepEqual(snapshot.captureSkewerMetadata(f.slots.get(hand==='off'?'off':0)),rows[1].native);
 });
 for(const target of ['hand', 'property', 'block'])test('take '+hand+' '+target+' post-write rejection restores ownership',()=>{
  const f=fixture();f.rows(2);const old=f.dp.get(f.key);f.oneFailure(target==='property'?f.key:target);
  f.api.handlePlateBlock(f.block,f.holder,hand);assert.equal(f.dp.get(f.key),old);assert.equal(f.slots.get(hand==='off'?'off':0),undefined);assert.equal(f.block.permutation.getState(N+'plate_count'),2);
 });
 test('inserting '+hand+' rolls back saved rows and original stack count on debit rejection',()=>{
  const f=fixture();f.rows(1);const old=f.dp.get(f.key),s=food();s.amount=3;f.slots.set(hand==='off'?'off':0,s);f.holder.isSneaking=false;f.oneFailure('hand');
  f.api.handlePlateBlock(f.block,f.holder,hand);assert.equal(f.dp.get(f.key),old);assert.equal(f.slots.get(hand==='off'?'off':0).amount,3);
 });
 for(const target of ['hand','property','block'])test('placement '+hand+' '+target+' rejection restores replaceable block, saved absence and source',()=>{
  const f=fixture();f.block.setType('minecraft:short_grass');const s=food();f.slots.set(hand==='off'?'off':0,s);f.oneFailure(target==='property'?f.key:target);
  assert.equal(f.api.placePlateOn({typeId:'minecraft:stone',x:0,y:79,z:0,dimension:f.block.dimension},'up',f.holder,s,hand),false);
  assert.equal(f.block.typeId,'minecraft:short_grass');assert.equal(f.dp.has(f.key),false);assert.deepEqual(snapshot.captureSkewerMetadata(f.slots.get(hand==='off'?'off':0)),snapshot.captureSkewerMetadata(s));
 });
}
test('successful placement faces west and creative placement retains source',()=>{
 for(const creative of [false,true]){const f=fixture();f.block.setType('minecraft:air');const s=food();f.slots.set(0,s);f.holder.creative=creative;
  assert.equal(f.api.placePlateOn({typeId:'minecraft:stone',x:0,y:79,z:0,dimension:f.block.dimension},'up',f.holder,s),true);
  assert.equal(f.block.permutation.getState('minecraft:cardinal_direction'),'west');assert.equal(f.api.readPlateBlock(f.block).length,1);assert.equal(!!f.slots.get(0),creative);
 }
});
test('orphaned data prevents overwriting a removed plate location',()=>{
 const f=fixture();f.rows(1);const old=f.dp.get(f.key);f.block.setType('minecraft:air');f.slots.set(0,food());
 assert.throws(()=>f.api.placePlateOn({typeId:'minecraft:stone',x:0,y:79,z:0,dimension:f.block.dimension},'up',f.holder,f.slots.get(0)),/orphaned/);assert.equal(f.dp.get(f.key),old);assert.equal(f.block.typeId,'minecraft:air');
});
test('incomplete rollback persists quarantine and blocks later reads/transfers',()=>{
 const f=fixture();f.rows(1);f.fault=k=>k==='hand';assert.throws(()=>f.api.handlePlateBlock(f.block,f.holder),/recovery required/);
 const key=f.api.plateFaultKey(f.block);assert.ok(f.dp.has(key));f.fault=undefined;assert.throws(()=>f.api.readPlateBlock(f.block),/quarantined/);
});
test('native hand adapter pins original slot for read, apply and rollback',()=>{
 const ioSource=fs.readFileSync(new URL('a2735_player_io.js',base),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const))/g,'');
 const rows=new Map([[3,food()],[4,new Stack('minecraft:stone')]]),io=vm.createContext({EquipmentSlot:{Offhand:'off'}});
 vm.runInContext(ioSource+'\nglobalThis.capture=captureWritableHand;',io);
 const holder={selectedSlotIndex:3,getComponent:()=>({container:{size:36,getItem:k=>rows.get(k),setItem:(k,v)=>rows.set(k,v)}})};
 const bound=io.capture(holder,'main'),after=food();after.amount=2;
 holder.selectedSlotIndex=4;
 const step=tx.verifiedPlateStep({read:bound.read,write:bound.write,before:bound.before,after,signature:s=>s?JSON.stringify(s):''});
 step.apply();assert.equal(rows.get(3).amount,2);step.rollback();assert.equal(rows.get(3).amount,1);assert.equal(rows.get(4).typeId,'minecraft:stone');
});
test('pre-write conflict preserves changed input instead of rolling it back',()=>{
 let value='other';const step=tx.verifiedPlateStep({read:()=>value,write:v=>{value=v},before:'old',after:'new'});
 assert.equal(tx.commitPlateSteps([step],()=>assert.fail()).ok,false);assert.equal(value,'other');
});

test('breaking a full plate delivers one packed item containing all native snapshots',()=>{
 const f=fixture(),rows=f.rows(5);assert.equal(f.api.breakPlate(f.block),true);
 assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.dp.has(f.key),false);const live=f.entities.filter(e=>e.isValid);assert.equal(live.length,1);
 assert.deepEqual(JSON.parse(item.getItemProperty(live[0].stack,plate.PLATE_SKEWERS_KEY)).map(r=>r.native),rows.map(r=>r.native));
 assert.equal(f.api.breakPlate(f.block),false);assert.equal(f.entities.filter(e=>e.isValid).length,1);
});
for(const target of ['dropRead','property','remove'])test('break '+target+' failure preserves plate and removes provisional drop',()=>{
 const f=fixture();f.rows(3);const raw=f.dp.get(f.key),state=JSON.stringify(f.block.permutation.getAllStates());f.oneFailure(target==='property'?f.key:target);
 assert.equal(f.api.breakPlate(f.block),false);assert.equal(f.block.typeId,PLATE);assert.equal(f.dp.get(f.key),raw);assert.equal(JSON.stringify(f.block.permutation.getAllStates()),state);assert.equal(f.entities.filter(e=>e.isValid).length,0);
});
test('spawn exception leaves contents intact and persists quarantine instead of retrying',()=>{
 const f=fixture();f.rows(2);const raw=f.dp.get(f.key);f.oneFailure('spawn');assert.equal(f.api.breakPlate(f.block),false);assert.equal(f.dp.get(f.key),raw);assert.equal(f.block.typeId,PLATE);
 assert.ok(f.dp.has(f.api.plateFaultKey(f.block)));assert.throws(()=>f.api.breakPlate(f.block),/quarantined/);assert.equal(f.entities.length,1);
});
test('creative and empty plate breaks do not generate a packed plate',()=>{
 for(const creative of [false,true]){const f=fixture();if(creative)f.rows(2);f.holder.creative=creative;assert.equal(f.api.breakPlate(f.block,f.holder),true);assert.equal(f.entities.length,0);assert.equal(f.dp.has(f.key),false);assert.equal(f.block.typeId,'minecraft:air');}
});
test('explosion callback removes only plate blocks from native destruction',()=>{
 const f=fixture();f.rows(2);const other={typeId:'minecraft:stone'};let kept;
 f.events.explosion({getImpactedBlocks:()=>[other,f.block],setImpactedBlocks:r=>{kept=r}});
 assert.equal(kept.length,1);assert.equal(kept[0],other);assert.equal(f.dp.has(f.key),true); // Before-event only schedules the actual transaction.
});

test('unconfirmed provisional drop cleanup blocks later break retries',()=>{
 const f=fixture();f.rows(2);const raw=f.dp.get(f.key);let propertyOnce=true;
 f.fault=k=>k==='dropRemoveBefore'||(k===f.key&&propertyOnce?(propertyOnce=false,true):false);
 assert.throws(()=>f.api.breakPlate(f.block),/recovery required/);assert.equal(f.dp.get(f.key),raw);assert.equal(f.entities.filter(e=>e.isValid).length,1);
 f.fault=undefined;assert.throws(()=>f.api.breakPlate(f.block),/quarantined/);assert.equal(f.entities.length,1);
});
