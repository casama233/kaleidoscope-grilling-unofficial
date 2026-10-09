/** Contract and fault-injection tests use storage doubles, never engine actors. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as oil from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/oil_api_core.js';
import * as food from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import * as quality from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/cuisine_quality_core.js';
import {registerSecretIngredientBehavior,applySecretBehaviorExtension,resetSecretCompatRegistry} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/secret_compat_core.js';
const base='projects/grilling/gameplay_core/behavior_pack/scripts/';
class Item{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.lore=[];this.props={};}isStackableWith(other){return this.maxAmount!==1&&other?.maxAmount!==1&&this.typeId===other?.typeId&&this.nameTag===other?.nameTag&&JSON.stringify(this.lore)===JSON.stringify(other?.lore)&&JSON.stringify(this.props)===JSON.stringify(other?.props)}getRawLore(){return structuredClone(this.lore)}setLore(v){this.lore=structuredClone(v)}getDynamicProperty(k){return this.props[k]}getDynamicPropertyIds(){return Object.keys(this.props)}setDynamicProperty(k,v){if(v===undefined)delete this.props[k];else this.props[k]=v}clone(){const n=new Item(this.typeId,this.amount);Object.assign(n,structuredClone({...this}));return n}}
class Slot{constructor(item){this.item=item?.clone();this.fail=0}hasItem(){return !!this.item}getItem(){return this.item?.clone()}setItem(s){if(this.fail-->0)throw Error('slot write fault');this.item=s?.clone()}}
function fixture(name,savedProperties){const properties=new Map(savedProperties),faults=new Map(),emitted=[],subscriptions={},drops=[];
 const signal=key=>({subscribe(fn){(subscriptions[key]??=[]).push(fn)}});
 const world={getDynamicProperty:k=>properties.get(k),setDynamicProperty(k,v){if(faults.get(k)){faults.set(k,faults.get(k)-1);throw Error('property fault')}if(v===undefined)properties.delete(k);else properties.set(k,v)},getAbsoluteTime:()=>1000,getAllPlayers:()=>[],getEntity:id=>drops.find(d=>d.id===id),afterEvents:{playerSpawn:signal('spawn'),playerPlaceBlock:signal('place')},beforeEvents:{playerInteractWithBlock:signal('interact'),playerBreakBlock:signal('break'),explosion:signal('explosion')}};
 const system={currentTick:100,run(){},runTimeout(){},afterEvents:{scriptEventReceive:signal('script')},sendScriptEvent:(id,message)=>emitted.push({id,data:JSON.parse(message)})};
 const ctx={...oil,...food,...quality,world,system,ItemStack:Item,EquipmentSlot:{Mainhand:'Mainhand',Offhand:'Offhand'},GameMode:{Creative:'Creative'},console};
 let code=fs.readFileSync(base+'host_api/'+name,'utf8').replace(/^import .*;\n/gm,'').replace(/\bexport /g,'');code+='\nthis.api={'+(name==='oil_api_host.js'?'consumeSharedOilFromHeldPot,readHostOilItem,readSharedPlacedOil,writeSharedPlacedOil,consumeSharedOilSlot,fillSharedPlacedOil,recoverSharedOilPot,retrySharedOilRecovery,commitSharedStationOil,publishLegacyHostOil':'deliverCuisineOutput,readCuisineMetadata,recoverCuisineOutput,nextCuisineBatch,prepareCuisineBurn')+'};';vm.runInNewContext(code,ctx);
 const dim={id:'minecraft:overworld',getBlock:()=>block,spawnItem(s){const item=s.clone(),d={id:'drop'+drops.length,getComponent:()=>({itemStack:item}),remove(){drops.splice(drops.indexOf(d),1)}};drops.push(d);return d}};
 const block={dimension:dim,x:40,y:80,z:64,typeId:oil.EMPTY_POT,permutation:{getState:()=>false,withState(_k,v){this.getState=()=>v;return this}},setPermutation(p){this.permutation=p}};
 return {api:ctx.api,properties,faults,emitted,drops,block,Slot,emitScript(event){for(const fn of subscriptions.script??[])fn(event)}};}
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

// G120 receipt regressions use the existing storage-only adapters. No player
// object, native interaction event or simulated-player API is constructed.
test('unacknowledged cuisine preparation and batch reservation cannot authorize output',()=>{
 const f=fixture('cuisine_api_host.js'),items=[],container={size:1,getItem:i=>items[i],setItem(i,s){items[i]=s}},write=f.properties.set.bind(f.properties);
 f.properties.set=(key,value)=>key.startsWith('senluo:cuisine_output:')?f.properties:write(key,value);
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',{container,targetBlock:f.block,operationId:'prepare-readback'}),/readback/);
 assert.throws(()=>f.api.nextCuisineBatch(f.block),/readback/);
 assert.equal(items.filter(Boolean).length,0);assert.equal(f.drops.length,0);
});
test('unconfirmed cuisine slot rollback stays quarantined without another credit',()=>{
 const f=fixture('cuisine_api_host.js'),items=[];let writes=0;
 const container={size:1,getItem:i=>items[i]?.clone(),setItem(i,s){if(++writes===1){items[i]=s.clone();throw Error('credit written')}/* ignored rollback */}};
 const options={container,targetBlock:f.block,operationId:'rollback-readback'},receiptKey='senluo:cuisine_output:minecraft:overworld:40,80,64:rollback-readback';
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options),error=>error.deliveryOutcomeUnknown===true);
 assert.equal(JSON.parse(f.properties.get(receiptKey)).phase,'quarantined');assert.equal(items[0].amount,1);
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options),/quarantined/);assert.equal(writes,2);
});
test('native custom-data disagreement cannot acknowledge or erase an output with the same public fingerprint',()=>{
 for(const destination of ['slot','entity']){
  const f=fixture('cuisine_api_host.js'),items=[],options={operationId:'native-ownership-'+destination};
  if(destination==='slot')Object.assign(options,{targetBlock:f.block,container:{size:1,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone();if(items[i])items[i].props['foreign:data']='different'}}});
  else{const spawn=f.block.dimension.spawnItem.bind(f.block.dimension);f.block.dimension.spawnItem=s=>{const d=spawn(s);d.getComponent().itemStack.props['foreign:data']='different';return d};}
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options),error=>error.deliveryOutcomeUnknown===true);
  const retained=items[0]??f.drops[0]?.getComponent().itemStack;assert.equal(retained?.props['foreign:data'],'different');
  const receiptKey='senluo:cuisine_output:minecraft:overworld:40,80,64:'+options.operationId;
  assert.equal(JSON.parse(f.properties.get(receiptKey)).phase,'quarantined');
 }
 const f=fixture('cuisine_api_host.js'),single=new Item('qa:single_food');single.maxAmount=1;
 assert.equal(f.api.deliverCuisineOutput(f.block,{},single.typeId,1,'pot',{nativeStack:single,operationId:'nonstackable-ack'}).phase,'committed');
 assert.equal(f.drops.length,1);
});
test('prepared cuisine receipt cannot use another recipient container as delivery evidence',()=>{
 const f=fixture('cuisine_api_host.js'),items=[],container={size:1,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}},write=f.properties.set.bind(f.properties);
 const receiptKey='senluo:cuisine_output:minecraft:overworld:40,80,64:recipient';let receipts=0;
 f.properties.set=(key,value)=>{if(key===receiptKey&&++receipts===2)throw Error('commit unavailable');return write(key,value)};
 const options={container,playerId:'recipient-a',operationId:'recipient'};
 assert.equal(f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options).recoveryPending,true);
 const other={size:1,getItem:()=>items[0].clone(),setItem(){throw Error('unrelated container must remain untouched')}};
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',{...options,container:other,playerId:'recipient-b'}),/unresolved/);
 assert.equal(f.api.deliverCuisineOutput(f.block,{},'qa:food',1,'pot',options).replayed,true);
});
test('takeout credit and destruction share the same saved portion count without losing its remainder',()=>{
 const f=fixture('cuisine_api_host.js'),items=[],container={size:1,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}};
 const data={result:{id:'qa:food',count:3},grillingOutputEpoch:77};
 f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{container,targetBlock:f.block,operationId:'pot:77:3'});
 // Exercise an existing committed receipt from before settlementVersion was
 // introduced. Its one acknowledged portion remains authoritative.
 const receiptKey='senluo:cuisine_output:minecraft:overworld:40,80,64:pot:77:3',prior=JSON.parse(f.properties.get(receiptKey));delete prior.settlementVersion;delete prior.kind;f.properties.set(receiptKey,JSON.stringify(prior));
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);
 assert.equal(items[0].amount,1);assert.equal(f.drops.length,1);assert.equal(f.drops[0].getComponent().itemStack.amount,2);
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.drops.length,1);
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,{...data,result:{...data.result,count:2}},'qa:food',1,'pot',{operationId:'pot:77:2'}),/destruction retained/);
 data.result.count=1;data.grillingOutputEpoch=78;
 f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:78:1'});
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.drops.length,2);
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:78:1'}),/destruction retained/);
});
test('unknown or legacy-unverified takeout rollback cannot become a destruction payout',()=>{
 for(const prior of [{phase:'prepared',settlementVersion:1},{phase:'quarantined',settlementVersion:1},{phase:'rolled_back'}]){
  const f=fixture('cuisine_api_host.js'),data={result:{id:'qa:food',count:3},grillingOutputEpoch:79};
  f.properties.set('senluo:cuisine_output:minecraft:overworld:40,80,64:pot:79:3',JSON.stringify({...prior,output:{id:'qa:food',amount:1}}));
  assert.throws(()=>f.api.recoverCuisineOutput(f.block,data),/unresolved/);assert.equal(f.drops.length,0);assert.equal(data.result.count,3);
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:79:2'}),/destruction retained/);
 }
});
test('committed legacy destruction fences its entire epoch while a new batch remains usable',()=>{
 const f=fixture('cuisine_api_host.js'),data={result:{id:'qa:food',count:2},grillingOutputEpoch:80};
 f.properties.set('senluo:cuisine_output:minecraft:overworld:40,80,64:break:pot:80:3',JSON.stringify({phase:'committed',output:{id:'qa:food',amount:3}}));
 assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:80:2'}),/destruction retained/);
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.drops.length,0);
 const fresh={result:{id:'qa:food',count:1},grillingOutputEpoch:81};
 assert.equal(f.api.deliverCuisineOutput(f.block,fresh,'qa:food',1,'pot',{operationId:'pot:81:1'}).phase,'committed');assert.equal(f.drops.length,1);
});
test('prepared destruction with an acknowledged drop only settles its fence on retry',()=>{
 const f=fixture('cuisine_api_host.js'),data={result:{id:'qa:food',count:2},grillingOutputEpoch:82},write=f.properties.set.bind(f.properties);let fences=0;
 f.properties.set=(key,value)=>{if(key==='senluo:cuisine_recovery:minecraft:overworld:40,80,64:pot:82'&&++fences===2)throw Error('terminal fence unavailable');return write(key,value)};
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.drops.length,1);
 assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.drops.length,1);
});
test('an existing nonobject recovery fence cannot be mistaken for an unused batch',()=>{
 for(const raw of ['null','false','0',false,0,'{}','[]']){
  const f=fixture('cuisine_api_host.js'),data={result:{id:'qa:food',count:2},grillingOutputEpoch:83};
  f.properties.set('senluo:cuisine_recovery:minecraft:overworld:40,80,64:pot:83',raw);
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:83:2'}),/recovery fence/);
  assert.throws(()=>f.api.recoverCuisineOutput(f.block,data),/recovery fence/);assert.equal(f.drops.length,0);
 }
});
test('charcoal takeout and break share one plain receipt and fence stale food from the same epoch',()=>{
 for(const first of ['takeout','break']){
  const f=fixture('cuisine_api_host.js'),items=[],container={size:1,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}};
  const data={burnt:true,charcoalCount:3,grillingOutputEpoch:84,grillingBurnOrigin:{version:1,epoch:84,resultId:'qa:food',sourceCount:3}};
  const collect=()=>f.api.deliverCuisineOutput(f.block,data,'minecraft:charcoal',3,'burnt',{container,targetBlock:f.block,operationId:'burnt:pot:84'});
  if(first==='takeout'){collect();assert.equal(f.api.recoverCuisineOutput(f.block,data),true)}
  else{assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(collect().replayed,true)}
  assert.equal(items.filter(Boolean).length+f.drops.length,1);
  const output=items[0]??f.drops[0].getComponent().itemStack;
  assert.equal(output.amount,3);assert.deepEqual(output.getRawLore(),[]);assert.equal(food.readPublicFood(output).present,false);assert.equal(f.emitted.length,0);
  const stale={result:{id:'qa:food',count:2},grillingOutputEpoch:84};
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,stale,'qa:food',1,'pot',{operationId:'pot:84:2'}),/burnt batch retained/);
  assert.throws(()=>f.api.recoverCuisineOutput(f.block,stale),/burnt batch retained/);
 }
});
// G121 regression: storage receipts only; no player or interaction adapter.
test('only a verified zero-credit original dish may rebind to its saved burnt dish',()=>{
 const original='kaleidoscope_grilling:braised_chicken_wings',dark='kaleidoscope_cookery:dark_cuisine',operationId='pot:904:1';
 function failedOriginal(){
  const f=fixture('cuisine_api_host.js'),result={id:original,count:1,carrier:'minecraft:bowl'};
  const data={grillingOutputEpoch:904,result,grillingPot:{version:1,epoch:904,phase:'finished',quality:0,output:result}};
  const rejected={size:1,getItem:()=>undefined,setItem(){throw Error('uncredited output')}};
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,original,1,'pot',{container:rejected,targetBlock:f.block,operationId}));
  const receiptKey='senluo:cuisine_output:minecraft:overworld:40,80,64:'+operationId;
  assert.equal(JSON.parse(f.properties.get(receiptKey)).phase,'rolled_back');
  let stored=JSON.stringify(data);f.api.prepareCuisineBurn(f.block,data,{raw:()=>stored,save(_b,next){stored=JSON.stringify(next)}});
  assert.equal(data.grillingBurnOrigin.quality,0);
  data.result={id:dark,count:1,carrier:'minecraft:bowl'};data.grillingPot.output=data.result;data.grillingPot.phase='burnt';delete data.grillingPot.quality;
  return {f,data,receiptKey};
 }
 for(const first of ['takeout','break']){
  const {f,data}=failedOriginal();
  if(first==='takeout')assert.equal(f.api.deliverCuisineOutput(f.block,data,dark,1,'pot',{operationId}).phase,'committed');
  assert.equal(f.api.recoverCuisineOutput(f.block,data),true);assert.equal(f.api.recoverCuisineOutput(f.block,data),true);
  assert.equal(f.drops.length,1);const output=f.drops[0].getComponent().itemStack;
  assert.equal(output.typeId,dark);assert.equal(food.readPublicFood(output).state.quality,undefined);assert.equal(food.readPublicFood(output).state.hotUntil,0);
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,dark,1,'pot',{operationId}),/destruction retained/);
 }
 for(const phase of ['prepared','committed','quarantined','mismatched_quality']){
  const {f,data,receiptKey}=failedOriginal(),receipt=JSON.parse(f.properties.get(receiptKey));
  if(phase==='mismatched_quality')data.grillingBurnOrigin.quality=3;else receipt.phase=phase;
  f.properties.set(receiptKey,JSON.stringify(receipt));
  assert.throws(()=>f.api.deliverCuisineOutput(f.block,data,dark,1,'pot',{operationId}),/conflict/);
  assert.throws(()=>f.api.recoverCuisineOutput(f.block,data),/conflict/);assert.equal(f.drops.length,0);
 }
});
test('burn origin is saved before result loss and an acknowledged old takeout cannot become charcoal',()=>{
 const f=fixture('cuisine_api_host.js'),active={items:['qa:ingredient'],recipe:{result:'qa:food',count:1},started:true};let stored=JSON.stringify(active);
 const host={raw:()=>stored,save(_b,next){stored=JSON.stringify(next)}};
 f.properties.set('senluo:cuisine_output:minecraft:overworld:40,80,64:break:pot:legacy:1',JSON.stringify({phase:'committed',output:{id:'qa:previous_food',amount:1}}));
 f.api.prepareCuisineBurn(f.block,active,host);assert.equal(active.grillingOutputEpoch,1);assert.equal(active.grillingBurnOrigin.sourceCount,0);assert.equal(JSON.parse(stored).grillingOutputEpoch,1);
 const ignored={items:['qa:ingredient'],recipe:{result:'qa:food',count:1},started:true},before=JSON.stringify(ignored);
 assert.throws(()=>f.api.prepareCuisineBurn(f.block,ignored,{raw:()=>before,save(){}}),/save readback/);assert.equal(ignored.grillingOutputEpoch,undefined);
 const data={result:{id:'qa:food',count:3},grillingOutputEpoch:85};
 f.api.deliverCuisineOutput(f.block,data,'qa:food',1,'pot',{operationId:'pot:85:3'});
 assert.throws(()=>f.api.prepareCuisineBurn(f.block,data,{raw:()=>JSON.stringify(data),save(){throw Error('credited source must remain intact')}}),/takeout retained/);
 assert.equal(data.result.count,3);assert.equal(data.grillingBurnOrigin,undefined);
 const legacy={burnt:true,charcoalCount:2,grillingOutputEpoch:85};
 assert.throws(()=>f.api.recoverCuisineOutput(f.block,legacy,{raw:()=>JSON.stringify(legacy),save(){}}),/legacy burnt food outcome retained/);
 assert.equal(f.drops.length,1);
});
test('custom food inherits all containers, effects and chili damage without duplicating base effects',()=>{
 resetSecretCompatRegistry();assert(registerSecretIngredientBehavior({input:'qa:food',behavior:{mode:'replace',effects:[{effect:'speed',ticks:200}],convertTo:'minecraft:bowl',remainders:[{id:'minecraft:flower_pot',count:1},{id:'minecraft:blue_ice',count:1}],damage:2}}));
 const b=applySecretBehaviorExtension({effects:[{effect:'speed',ticks:200}]},{id:'qa:food'});assert.equal(b.effects.length,1);assert.equal(b.remainders.length,2);assert.equal(b.convertTo,'minecraft:bowl');assert.equal(b.damage,2);
});

test('station oil save failure restores the native slot and state before retry',()=>{
 const f=fixture('oil_api_host.js'),slot=new Slot(oil.createPublicOilPot(Item,'secret_chili',8));let stored={},once=true;
 const data={},host={save(_b,s){stored=structuredClone(s);if(once){once=false;throw Error('station save')}},load:()=>stored,raw:()=>Object.keys(stored).length?JSON.stringify(stored):undefined,sync(){}};
 assert.throws(()=>f.api.commitSharedStationOil(f.block,slot,data,host),/station save/);assert.equal(oil.readPublicOil(slot.getItem()).state.count,8);assert.deepEqual(stored,{});
 assert.equal(f.api.commitSharedStationOil(f.block,slot,data,host).ok,true);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);assert.equal(stored.oilTicks,12000);assert.equal(stored.grillingOilType,'secret_chili');
});

// Ownership/slot objects below are storage adapters, not simulated engine players.
const owner=(slot,id='owner-a')=>({id,getGameMode:()=> 'Survival',getComponent:()=>({getEquipmentSlot:()=>slot})});
const ownerKey=id=>'senluo:oil_hand_fault:'+id;
function stationHost(){let stored={};return {get stored(){return stored},save(_b,s){stored=structuredClone(s)},load:()=>stored,raw:()=>Object.keys(stored).length?JSON.stringify(stored):undefined,sync(){}}}
for(const mode of ['throws','silently-wrong'])test('partial hand debit with '+mode+' rollback blocks both routes and survives restart',()=>{
 const f=fixture('oil_api_host.js');let calls=0;
 class Broken extends Slot{setItem(s){calls++;if(calls===1){this.item=s.clone();throw Error('debit applied')}if(calls===2){if(mode==='throws')throw Error('restore rejected');this.item=s.clone();this.item.props['foreign:data']='lost';return}super.setItem(s)}}
 const original=oil.createPublicOilPot(Item,'secret_chili',8);original.props['foreign:data']='keep';const slot=new Broken(original),h=stationHost();
 const r=f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'});assert.equal(r.ok,false);assert.equal(r.recoveryRequired,true);assert.deepEqual(h.stored,{});assert.ok(f.properties.has(ownerKey('owner-a')));
 const before=calls;assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),false);assert.equal(calls,before);
 const g=fixture('oil_api_host.js',f.properties);g.block.x=41;const otherSlot=new Slot(oil.createPublicOilPot(Item,'premium_chili',20));
 assert.equal(g.api.commitSharedStationOil(g.block,otherSlot,{},stationHost(),{ownerId:'owner-a'}).ok,false);
 assert.equal(g.api.consumeSharedOilFromHeldPot(owner(otherSlot)),false);assert.equal(oil.readPublicOil(otherSlot.getItem()).state.count,20);
 assert.equal(g.api.consumeSharedOilFromHeldPot(owner(otherSlot,'owner-b')),true);assert.equal(oil.readPublicOil(otherSlot.getItem()).state.count,19);
});
test('legacy count lost during acknowledged rollback is quarantined, never retried as full256',()=>{
 const f=fixture('oil_api_host.js'),legacy=new Item(oil.FILLED_POT);legacy.props.kc_oil_count=32;let writes=0,saves=0;
 class DropsCount extends Slot{setItem(s){super.setItem(s);if(++writes===2)delete this.item.props.kc_oil_count}}
 const slot=new DropsCount(legacy),h=stationHost(),save=h.save;h.save=(b,d)=>{save(b,d);if(++saves===1)throw Error('station rejected')};
 assert.throws(()=>f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'}),/station rejected/);assert.deepEqual(h.stored,{});assert.ok(f.properties.has(ownerKey('owner-a')));
 assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),false);assert.equal(writes,2);
});
test('failed rollback of hand still attempts station restoration and retains owner journal',()=>{
 const f=fixture('oil_api_host.js');let writes=0,saves=0;
 class Broken extends Slot{setItem(s){if(++writes===2)throw Error('hand rollback');super.setItem(s)}}
 const slot=new Broken(oil.createPublicOilPot(Item,'canola',8)),h=stationHost(),save=h.save;h.save=(b,d)=>{save(b,d);if(++saves===1)throw Error('station after-write')};
 assert.throws(()=>f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'}));assert.equal(saves,2);assert.deepEqual(h.stored,{});assert.ok(f.properties.has(ownerKey('owner-a')));
 assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),false);
});
test('exact hand rollback after a post-write exception is retryable without lost oil',()=>{
 const f=fixture('oil_api_host.js');let once=true;
 class Once extends Slot{setItem(s){super.setItem(s);if(once){once=false;throw Error('after-write')}}}
 const slot=new Once(oil.createPublicOilPot(Item,'secret_chili',8)),h=stationHost();assert.equal(f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'}).ok,false);
 assert.equal(oil.readPublicOil(slot.getItem()).state.count,8);assert.ok(['committed','rolled_back'].includes(JSON.parse(f.properties.get(ownerKey('owner-a'))).phase));
 assert.equal(f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'}).ok,true);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);
});
for(const fault of ['write','readback'])test('prepared journal '+fault+' failure prevents any hand mutation',()=>{
 const f=fixture('oil_api_host.js'),k=ownerKey('owner-a');let writes=0;
 class Count extends Slot{setItem(s){writes++;super.setItem(s)}}
 if(fault==='write')f.faults.set(k,1);else{const get=f.properties.get.bind(f.properties);let reads=0;f.properties.get=key=>{if(key===k&&++reads===2)throw Error('receipt unreadable');return get(key)}}
 const slot=new Count(oil.createPublicOilPot(Item,'canola',8));assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),false);assert.equal(writes,0);assert.equal(oil.readPublicOil(slot.getItem()).state.count,8);
});
test('unresolved prepared owner journal blocks creative use without clearing it',()=>{
 const f=fixture('oil_api_host.js'),k=ownerKey('owner-a');f.properties.set(k,JSON.stringify({phase:'prepared'}));const slot=new Slot(oil.createPublicOilPot(Item,'canola',8));const p=owner(slot);p.getGameMode=()=> 'Creative';
 assert.equal(f.api.consumeSharedOilFromHeldPot(p),false);assert.ok(f.properties.has(k));assert.equal(oil.readPublicOil(slot.getItem()).state.count,8);
});
test('dynamic property enumeration failure prevents the debit',()=>{
 const f=fixture('oil_api_host.js');let writes=0;
 class Unreadable extends Item{getDynamicPropertyIds(){throw Error('unreadable properties')}clone(){const n=new Unreadable(this.typeId,this.amount);Object.assign(n,structuredClone({...this}));return n}}
 const bad=new Unreadable(oil.FILLED_POT);Object.assign(bad,oil.createPublicOilPot(Item,'canola',8));const slot=new Slot(bad);slot.setItem=()=>{writes++};
 const r=f.api.consumeSharedOilSlot(slot,1,false,{ownerId:'owner-a'});assert.equal(r.ok,false);assert.match(r.reason,/unreadable properties/);assert.equal(writes,0);
});
test('normal debit preserves type, revision and unrelated dynamic metadata and settles receipt',()=>{
 const f=fixture('oil_api_host.js'),s=oil.createPublicOilPot(Item,'premium_chili',8);s.props.kc_oil_count=256;s.props['foreign:data']='keep';s.props['foreign:vector']={x:1,y:2,z:3};const slot=new Slot(s);
 assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),true);const after=slot.getItem(),state=oil.readPublicOil(after).state;
 assert.equal(state.type,'premium_chili');assert.equal(state.count,7);assert.equal(state.revision,oil.readPublicOil(s).state.revision+1);assert.equal(after.props['foreign:data'],'keep');assert.deepEqual(after.props['foreign:vector'],{x:1,y:2,z:3});assert.ok(['committed','rolled_back'].includes(JSON.parse(f.properties.get(ownerKey('owner-a'))).phase));
});

for(const context of ['standalone','station'])test('acknowledged '+context+' operation is not rolled back for unreadable settlement journal',()=>{
 const f=fixture('oil_api_host.js'),k=ownerKey('owner-a'),get=f.properties.get.bind(f.properties);let reads=0,writes=0;
 f.properties.get=key=>{if(key===k&&++reads===3)throw Error('settlement readback unavailable');return get(key)};
 class Count extends Slot{setItem(s){if(++writes===2)throw Error('must not compensate acknowledged success');super.setItem(s)}}
 const slot=new Count(oil.createPublicOilPot(Item,'secret_chili',8)),h=stationHost();
 const r=context==='standalone'?f.api.consumeSharedOilSlot(slot,1,false,{ownerId:'owner-a'}):f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'owner-a'});
 assert.equal(r.ok,true);assert.equal(r.recoveryPending,true);assert.equal(writes,1);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);if(context==='station')assert.equal(h.stored.oil,true);
 assert.equal(JSON.parse(get(k)).phase,'committed');assert.equal(f.api.consumeSharedOilFromHeldPot(owner(slot)),false);assert.equal(writes,1);
 // Reload sees an acknowledged terminal receipt, never an uncredited failure.
 const fresh=fixture('oil_api_host.js',f.properties);assert.equal(JSON.parse(fresh.properties.get(k)).phase,'committed');
});
test('failed terminal receipt write retains durable prepared owner guard after credited debit',()=>{
 const f=fixture('oil_api_host.js'),k=ownerKey('owner-a'),set=f.properties.set.bind(f.properties);let calls=0;
 f.properties.set=(key,value)=>{if(key===k&&++calls===2)throw Error('settlement storage unavailable');return set(key,value)};
 const slot=new Slot(oil.createPublicOilPot(Item,'secret_chili',8)),r=f.api.consumeSharedOilSlot(slot,1,false,{ownerId:'owner-a'});
 assert.equal(r.ok,true);assert.equal(r.recoveryPending,true);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);assert.equal(JSON.parse(f.properties.get(k)).phase,'prepared');
 const fresh=fixture('oil_api_host.js',f.properties);assert.equal(fresh.api.consumeSharedOilFromHeldPot(owner(slot)),false);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);
});

test('author snapshot certifies an unrecorded legacy filled pot as 256 while retaining strict public validation',()=>{
 const f=fixture('oil_api_host.js'),legacy=new Item(oil.FILLED_POT);legacy.nameTag='Legacy filled';const next=f.api.publishLegacyHostOil(legacy);assert.equal(oil.readPublicOil(next).state.count,256);assert.equal(oil.readPublicOil(next).state.type,'');assert.equal(next.nameTag,'Legacy filled');
 legacy.props.kc_oil_count=32;assert.equal(oil.readPublicOil(f.api.publishLegacyHostOil(legacy)).state.count,32);
 const corrupt=oil.createPublicOilPot(Item,'canola',8);corrupt.lore.push(corrupt.lore.find(x=>typeof x==='string'&&x.includes('§r§0§r§3§r§6')));assert.throws(()=>f.api.publishLegacyHostOil(corrupt));
});

test('Cookery configuration disables only new heat and seasoning, persists across reload and re-enables',()=>{
 const f=fixture('cuisine_api_host.js');
 const metaKey='senluo:cuisine_metadata:minecraft:overworld:40,80,64';
 f.properties.set(metaKey,JSON.stringify({seasoning:['minecraft:redstone'],oilType:'premium_chili'}));
 const config=enabled=>({id:'kaleidoscope_cookery:cuisine_config',message:JSON.stringify({api:1,enabled})});
 f.emitScript(config(false));assert.deepEqual(JSON.parse(JSON.stringify(f.api.readCuisineMetadata(f.block))),{v:1,hotUntil:0,seasoning:[]});
 const out=f.api.deliverCuisineOutput(f.block,{},'minecraft:bread',1,'pot',{operationId:'disabled:1'});
 assert.equal(out.metadata.hotUntil,0);assert.equal(out.metadata.seasoning.length,0);
 assert.equal(f.drops.length,1);assert.equal(f.drops[0].getComponent().itemStack.getRawLore().some(row=>JSON.stringify(row).includes('smoky_warmth')),false);
 assert.equal(JSON.parse(f.properties.get(metaKey)).oilType,'premium_chili');
 const g=fixture('cuisine_api_host.js',f.properties);assert.equal(g.api.readCuisineMetadata(g.block).hotUntil,0);
 g.emitScript(config('true'));assert.equal(g.api.readCuisineMetadata(g.block).hotUntil,0);
 g.emitScript(config(true));assert.equal(g.api.readCuisineMetadata(g.block).hotUntil,25000);assert.equal(g.api.readCuisineMetadata(g.block).seasoning[0],'minecraft:redstone');
});

// Concrete conservation regression: a station still owning its credited oil
// after a rejected rollback cannot also refund the same oil point to the hand.
test('failed station compensation retains the oil debit and quarantines both owners',()=>{
 const f=fixture('oil_api_host.js'),h=stationHost(),save=h.save;let saves=0,writes=0;
 class Count extends Slot{setItem(s){writes++;super.setItem(s)}}
 const slot=new Count(oil.createPublicOilPot(Item,'canola',8));
 h.save=(b,data)=>{if(++saves===1){save(b,data);throw Error('station after-write')}throw Error('station rollback rejected')};
 assert.throws(()=>f.api.commitSharedStationOil(f.block,slot,{},h,{ownerId:'station-rollback'}),/station after-write/);
 assert.equal(h.stored.oil,true);assert.equal(oil.readPublicOil(slot.getItem()).state.count,7);assert.equal(writes,1);
 assert.equal(JSON.parse(f.properties.get(ownerKey('station-rollback'))).phase,'prepared');
 assert.ok(f.properties.has('senluo:oil_station_fault:minecraft:overworld:40,80,64'));
});
