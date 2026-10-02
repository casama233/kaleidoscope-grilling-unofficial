/** Contract and fault-injection tests use storage doubles, never engine actors. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as oil from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/oil_api_core.js';
import * as food from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import {registerSecretIngredientBehavior,applySecretBehaviorExtension,resetSecretCompatRegistry} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/secret_compat_core.js';
const base='projects/grilling/gameplay_core/behavior_pack/scripts/';
class Item{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.lore=[];this.props={};}getRawLore(){return structuredClone(this.lore)}setLore(v){this.lore=structuredClone(v)}getDynamicProperty(k){return this.props[k]}setDynamicProperty(k,v){if(v===undefined)delete this.props[k];else this.props[k]=v}clone(){const n=new Item(this.typeId,this.amount);Object.assign(n,structuredClone({...this}));return n}}
class Slot{constructor(item){this.item=item?.clone();this.fail=0}hasItem(){return !!this.item}getItem(){return this.item?.clone()}setItem(s){if(this.fail-->0)throw Error('slot write fault');this.item=s?.clone()}}
function fixture(name){const properties=new Map(),faults=new Map(),emitted=[],subscriptions={},drops=[];
 const signal=key=>({subscribe(fn){subscriptions[key]=fn}});
 const world={getDynamicProperty:k=>properties.get(k),setDynamicProperty(k,v){if(faults.get(k)){faults.set(k,faults.get(k)-1);throw Error('property fault')}if(v===undefined)properties.delete(k);else properties.set(k,v)},getAbsoluteTime:()=>1000,getAllPlayers:()=>[],getEntity:id=>drops.find(d=>d.id===id),afterEvents:{playerSpawn:signal('spawn'),playerPlaceBlock:signal('place')},beforeEvents:{playerInteractWithBlock:signal('interact'),playerBreakBlock:signal('break'),explosion:signal('explosion')}};
 const system={currentTick:100,run(){},runTimeout(){},afterEvents:{scriptEventReceive:signal('script')},sendScriptEvent:(id,message)=>emitted.push({id,data:JSON.parse(message)})};
 const ctx={...oil,...food,world,system,ItemStack:Item,EquipmentSlot:{Mainhand:'Mainhand',Offhand:'Offhand'},GameMode:{Creative:'Creative'},console};
 let code=fs.readFileSync(base+'host_api/'+name,'utf8').replace(/^import .*;\n/gm,'').replace(/\bexport /g,'');code+='\nthis.api={'+(name==='oil_api_host.js'?'readHostOilItem,readSharedPlacedOil,writeSharedPlacedOil,consumeSharedOilSlot,fillSharedPlacedOil,recoverSharedOilPot,retrySharedOilRecovery,commitSharedStationOil,publishLegacyHostOil':'deliverCuisineOutput,readCuisineMetadata')+'};';vm.runInNewContext(code,ctx);
 const dim={id:'minecraft:overworld',getBlock:()=>block,spawnItem(s){const item=s.clone(),d={id:'drop'+drops.length,getComponent:()=>({itemStack:item}),remove(){drops.splice(drops.indexOf(d),1)}};drops.push(d);return d}};
 const block={dimension:dim,x:40,y:80,z:64,typeId:oil.EMPTY_POT,permutation:{getState:()=>false,withState(_k,v){this.getState=()=>v;return this}},setPermutation(p){this.permutation=p}};
 return {api:ctx.api,properties,faults,emitted,drops,block,Slot};}
test('public oil debits once, host ignores stale private count, and every typed oil empties correctly',()=>{
 const f=fixture('oil_api_host.js');for(const type of ['','canola','secret_chili','premium_chili']){
  const s=oil.createPublicOilPot(Item,type,3);s.props.kc_oil_count=256;const slot=new Slot(s);
  assert.equal(f.api.consumeSharedOilSlot(slot,3).ok,true);assert.equal(slot.getItem().typeId,oil.EMPTY_POT);assert.equal(oil.readPublicOil(slot.getItem()).state.count,0);assert.equal(f.api.consumeSharedOilSlot(slot,1).ok,false);
 }
});
test('placed typed pots keep type/count, reject mixing, preserve contents on failed hand writes',()=>{
 const f=fixture('oil_api_host.js');f.api.writeSharedPlacedOil(f.block,{v:1,type:'canola',count:8,revision:1});
 const slot=new Slot(new Item('kaleidoscope_grilling:canola_oil_bucket'));
 assert.equal(f.api.fillSharedPlacedOil(f.block,slot,'secret_chili').ok,false);assert.equal(f.api.readSharedPlacedOil(f.block).count,8);
 slot.fail=1;assert.throws(()=>f.api.fillSharedPlacedOil(f.block,slot,'canola'));assert.equal(f.api.readSharedPlacedOil(f.block).count,8);assert.equal(slot.getItem().typeId,'kaleidoscope_grilling:canola_oil_bucket');
 assert.equal(f.api.fillSharedPlacedOil(f.block,slot,'canola').ok,true);assert.equal(f.api.readSharedPlacedOil(f.block).count,16);assert.equal(slot.getItem().typeId,'minecraft:bucket');
});
test('placed oil failures roll back both stores and quarantine failed rollback',()=>{
 const f=fixture('oil_api_host.js'),key='kc_oilpot:minecraft:overworld:40,80,64';f.api.writeSharedPlacedOil(f.block,{v:1,type:'premium_chili',count:8,revision:1});
 const slot=new Slot(new Item('kaleidoscope_grilling:premium_chili_oil_bucket'));f.faults.set(key,1);
 assert.throws(()=>f.api.fillSharedPlacedOil(f.block,slot,'premium_chili'));assert.equal(f.api.readSharedPlacedOil(f.block).count,8);assert.equal(slot.getItem().typeId,'kaleidoscope_grilling:premium_chili_oil_bucket');
 f.faults.set(key,2);assert.throws(()=>f.api.fillSharedPlacedOil(f.block,slot,'premium_chili'));assert.throws(()=>f.api.readSharedPlacedOil(f.block),/unresolved/);
});
test('each author output carries seasonings and oil heat through the actual target and repeat delivery',()=>{
 for(const [type,ticks] of [['',1200],['secret_chili',12000],['premium_chili',24000]]){
  const f=fixture('cuisine_api_host.js'),items=Array(3),container={size:3,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}};
  f.properties.set('senluo:cuisine_metadata:minecraft:overworld:40,80,64',JSON.stringify({seasoning:['minecraft:redstone'],oilType:type}));
  const options={container,targetBlock:f.block,operationId:'pot:1:1'},r=f.api.deliverCuisineOutput(f.block,{grillingOilType:type},'qa:food',1,'pot',options);
  assert.equal(food.readPublicFood(items[r.target.slot]).state.hotUntil,1000+ticks);assert.deepEqual(food.readPublicFood(items[r.target.slot]).state.seasoning,['minecraft:redstone']);
  assert.equal(f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options).replayed,true);assert.equal(items.filter(Boolean).length,1);
 }
});
test('unknown prepared output is retained without another credit; acknowledged journal failure cannot double credit',()=>{
 const f=fixture('cuisine_api_host.js'),items=Array(3),container={size:3,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}};
 const options={container,targetBlock:f.block,operationId:'pot:2:1'},k='senluo:cuisine_output:minecraft:overworld:40,80,64:pot:2:1';
 f.properties.set(k,JSON.stringify({phase:'prepared',target:{kind:'block_slot',slot:0},output:{id:'qa:food',amount:1,lore:[]}}));
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options),/unresolved/);assert.equal(items.filter(Boolean).length,0);
 f.properties.delete(k);let calls=0;const write=f.properties.set.bind(f.properties);f.properties.set=(key,value)=>{if(key===k&&++calls===2)throw Error('commit journal');return write(key,value)};
 assert.equal(f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options).phase,'committed');f.properties.set=write;
 assert.equal(f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options).replayed,true);assert.equal(items.filter(Boolean).length,1);
});
test('custom food inherits all containers, effects and chili damage without duplicating base effects',()=>{
 resetSecretCompatRegistry();assert(registerSecretIngredientBehavior({input:'qa:food',behavior:{mode:'replace',effects:[{effect:'speed',ticks:200}],convertTo:'minecraft:bowl',remainders:[{id:'minecraft:flower_pot',count:1},{id:'minecraft:blue_ice',count:1}],damage:2}}));
 const b=applySecretBehaviorExtension({effects:[{effect:'speed',ticks:200}]},{id:'qa:food'});assert.equal(b.effects.length,1);assert.equal(b.remainders.length,2);assert.equal(b.convertTo,'minecraft:bowl');assert.equal(b.damage,2);
});

test('station oil save failure restores the native slot and state before retry',()=>{
 const f=fixture('oil_api_host.js'),slot=new Slot(oil.createPublicOilPot(Item,'secret_chili',8));let stored={},once=true;
 const data={},host={save(_b,s){stored=structuredClone(s);if(once){once=false;throw Error('station save')}},load:()=>stored,sync(){}};
 assert.throws(()=>f.api.commitSharedStationOil(f.block,slot,data,host),/station save/);assert.equal(oil.readPublicOil(slot.getItem()).state.count,8);assert.deepEqual(stored,{});
 assert.equal(f.api.commitSharedStationOil(f.block,slot,data,host).ok,true);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);assert.equal(stored.oilTicks,12000);assert.equal(stored.grillingOilType,'secret_chili');
});

test('author snapshot certifies an unrecorded legacy filled pot as 256 while retaining strict public validation',()=>{
 const f=fixture('oil_api_host.js'),legacy=new Item(oil.FILLED_POT);legacy.nameTag='Legacy filled';const next=f.api.publishLegacyHostOil(legacy);assert.equal(oil.readPublicOil(next).state.count,256);assert.equal(oil.readPublicOil(next).state.type,'');assert.equal(next.nameTag,'Legacy filled');
 legacy.props.kc_oil_count=32;assert.equal(oil.readPublicOil(f.api.publishLegacyHostOil(legacy)).state.count,32);
 const corrupt=oil.createPublicOilPot(Item,'canola',8);corrupt.lore.push(corrupt.lore.find(x=>typeof x==='string'&&x.includes('§r§0§r§3§r§6')));assert.throws(()=>f.api.publishLegacyHostOil(corrupt));
});
