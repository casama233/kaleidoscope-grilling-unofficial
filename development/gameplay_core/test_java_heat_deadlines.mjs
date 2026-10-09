/** Production metadata modules with storage-operation adapters; no player/client claim. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {bucketHotUntil,readPublicFood,writePublicFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import {SEASONING_LIST_KEY} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
const oracle=JSON.parse(fs.readFileSync(new URL('./fixtures/java-heat-deadlines.json',import.meta.url)));
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
async function fixture(){
 let tick=1099;const props=new Map(),context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Math,Boolean,Error,Date});
 const world={getAbsoluteTime:()=>tick,getDynamicProperty:k=>props.get(k),setDynamicProperty:(k,v)=>v===undefined?props.delete(k):props.set(k,v)};
 const system={get currentTick(){return tick},run(){},sendScriptEvent(){},afterEvents:{scriptEventReceive:{subscribe(){}}}};
 const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',Stack);this.setExport('EquipmentSlot',{});this.setExport('GameMode',{Creative:'Creative'})},{context});
 // Tooltip event scheduling is unrelated to heat writes; its pure lore module is real.
 const tooltipEvents=new vm.SyntheticModule([],function(){},{context});
 const modules=new Map();
 function load(url){const id=url.href;if(!modules.has(id))modules.set(id,new vm.SourceTextModule(fs.readFileSync(url,'utf8'),{context,identifier:id}));return modules.get(id)}
 const adapter=load(new URL('a2750_food_state_adapter.js',root));
 await adapter.link((spec,parent)=>spec==='@minecraft/server'?server:spec==='./a2769_food_tooltip_runtime.js'?tooltipEvents:load(new URL(spec,parent.identifier)));
 await adapter.evaluate();
 const cuisine=load(new URL('host_api/cuisine_api_host.js',root));
 await cuisine.link((spec,parent)=>spec==='@minecraft/server'?server:load(new URL(spec,parent.identifier)));
 await cuisine.evaluate();
 const data=modules.get(new URL('itemDataCore.js',root).href).namespace;
 return {api:adapter.namespace,cuisine:cuisine.namespace,data,properties:props,setTick:v=>tick=v};
}
class Stack{
 constructor(maxAmount=64){this.typeId='minecraft:cooked_beef';this.maxAmount=maxAmount;this.amount=1;this.lore=[];this.dp=new Map()}
 getRawLore(){return structuredClone(this.lore)}setLore(v){if(v.length>20)throw Error('native lore capacity');this.lore=structuredClone(v)}
 getDynamicProperty(k){return this.dp.get(k)}getDynamicPropertyIds(){return [...this.dp.keys()]}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v);if(this.failOnce){this.failOnce=false;throw Error('post-write property fault')}}
 clone(){const s=new Stack(this.maxAmount);s.typeId=this.typeId;s.amount=this.amount;s.lore=this.getRawLore();s.dp=new Map(this.dp);s.nameTag=this.nameTag;return s}
}
test('all new heat deadlines match executed author Java bucket vectors',()=>{
 for(const v of oracle.vectors)assert.equal(bucketHotUntil(v.until),v.expected);
 for(const invalid of [-1,NaN,Infinity,1.5,Number.MAX_SAFE_INTEGER+1])assert.throws(()=>bucketHotUntil(invalid));
});
test('new food deadlines use absolute Java buckets and legacy expiry reads stay precise',async()=>{
 const {api,data,setTick}=await fixture();
 for(const duration of [1,1200,12000,24000]){
  const s=new Stack();api.setHotFood(s,duration);
  assert.equal(api.hotUntil(s),bucketHotUntil(1099+duration));
  assert.equal(api.isHotFood(s),api.hotUntil(s)>1099);
 }
 const old=new Stack();data.setItemProperty(old,api.HOT_UNTIL_KEY,2277);
 assert.equal(api.hotUntil(old),2277);setTick(2276);assert.equal(api.isHotFood(old),true);
 setTick(2277);api.refreshHotLore(old);assert.equal(api.hotUntil(old),0);
});
test('nineteen user lines leave room for heat carrier while the cosmetic badge stays out',async()=>{
 const {api}=await fixture(),s=new Stack();s.setLore(Array.from({length:19},(_,i)=>({text:'keepsake '+i})));
 const before=s.getRawLore();api.setHotFood(s,1200);
 assert.equal(api.hotUntil(s),2200);assert.equal(s.getRawLore().length,20);
 assert.deepEqual(s.getRawLore().slice(0,19),before);api.refreshHotLore(s);assert.equal(s.getRawLore().length,20);
});
test('full stackable lore is preserved without a misleading badge; native data can still heat full lore',async()=>{
 const {api}=await fixture();for(const limit of [64,1]){
  const s=new Stack(limit);s.setLore(Array(20).fill('foreign line'));const before=s.getRawLore();api.setHotFood(s,1200);
  assert.deepEqual(s.getRawLore(),before);assert.equal(api.hotUntil(s),limit===1?2200:0);
 }
});
test('corrupt public food and native post-write faults retain original heat and raw lore',async()=>{
 const {api}=await fixture();
 const corrupt=new Stack();corrupt.lore=[{translate:'senluo.public.food.v1',with:['bad json']}];const old=corrupt.getRawLore();api.setHotFood(corrupt,1200);assert.deepEqual(corrupt.getRawLore(),old);
 const s=new Stack(1);s.lore=[{text:'foreign'}];s.dp.set(api.HOT_UNTIL_KEY,2277);s.failOnce=true;api.setHotFood(s,1200);
 assert.equal(api.hotUntil(s),2277);assert.deepEqual(s.getRawLore(),[{text:'foreign'}]);
});
test('existing public producers keep exact data on reads and mirror buckets only after new heating',async()=>{
 const {api}=await fixture(),s=new Stack();writePublicFood(s,{v:1,hotUntil:2277,seasoning:['minecraft:redstone'],nativeVariant:7});
 assert.equal(api.hotUntil(s),2277);api.setHotFood(s,1200);
 assert.equal(api.hotUntil(s),2200);assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:2200,seasoning:['minecraft:redstone'],nativeVariant:7});
});

test('absolute 100-tick boundaries include newly written deadlines at or before now',async()=>{
 const {api,setTick}=await fixture();
 for(const time of [1000,1099,1150])for(const ticks of [1,49,50,99,100,101,1200,12000,24000])for(const publicCarrier of [false,true]){
  setTick(time);const s=new Stack();
  if(publicCarrier)writePublicFood(s,{v:1,hotUntil:2277,seasoning:['minecraft:redstone'],nativeVariant:7});
  const expected=Math.floor((time+ticks)/100)*100;
  api.setHotFood(s,ticks);assert.equal(api.hotUntil(s),expected);
  assert.equal(api.isHotFood(s),expected>time);
  assert.equal(JSON.stringify(s.getRawLore()).includes('smoky_warmth'),expected>time);
  if(expected<=time){api.refreshHotLore(s);assert.equal(api.hotUntil(s),0)}
  if(publicCarrier)assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:expected>time?expected:0,seasoning:['minecraft:redstone'],nativeVariant:7});
 }
});

test('public and private carriers respect the 20-line limit without losing user lore',async()=>{
 const {api,data}=await fixture();
 for(const max of [64,1])for(const count of [18,19]){
  const s=new Stack(max),user=Array.from({length:count},(_,i)=>({text:'user '+i}));s.setLore(user);
  writePublicFood(s,{v:1,hotUntil:2277,seasoning:['minecraft:redstone'],nativeVariant:7});
  const before=s.getRawLore();api.setHotFood(s,1200);
  if(max===64&&count===19){
   // A public-only full stackable lore cannot add the required private carrier.
   assert.deepEqual(s.getRawLore(),before);assert.equal(api.hotUntil(s),2277);
  }else{
   assert.equal(api.hotUntil(s),2200);assert.equal(data.getItemProperty(s,api.HOT_UNTIL_KEY),2200);
   assert.deepEqual(s.getRawLore().slice(0,count),user);assert.ok(s.getRawLore().length<=20);
  }
  api.refreshHotLore(s);assert.deepEqual(s.getRawLore().slice(0,count),user);assert.ok(s.getRawLore().length<=20);
 }
});

test('host outputs preserve 19 user lines plus the public payload and skip the cosmetic badge',async()=>{
 const {cuisine,setTick,properties}=await fixture();
 const block={dimension:{id:'minecraft:overworld'},x:40,y:80,z:64};
 properties.set('senluo:cuisine_metadata:minecraft:overworld:40,80,64',JSON.stringify({seasoning:['minecraft:redstone'],oilType:'premium_chili'}));
 for(const time of [1000,1099,1150]){
  setTick(time);const native=new Stack(),user=Array.from({length:19},(_,i)=>({text:'host user '+i}));native.setLore(user);
  writePublicFood(native,{v:1,hotUntil:2277,seasoning:[],nativeVariant:7});const before=native.getRawLore(),items=[];
  const container={size:1,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone()}};
  const receipt=cuisine.deliverCuisineOutput(block,{},native.typeId,1,'pot',{container,targetBlock:block,nativeStack:native,operationId:'lore-limit:'+time});
  assert.equal(receipt.phase,'committed');assert.equal(items[0].getRawLore().length,20);
  assert.deepEqual(items[0].getRawLore().slice(0,19),user);assert.deepEqual(native.getRawLore(),before);
  assert.deepEqual(readPublicFood(items[0]).state,{v:1,hotUntil:Math.floor((time+24000)/100)*100,seasoning:['minecraft:redstone'],nativeVariant:7});
 }
});

const propertySnapshot=(data,s)=>JSON.stringify(data.getItemPropertyIds(s).sort().map(k=>[k,data.getItemProperty(s,k)]));
async function expiredFixture(max=64){
 const f=await fixture(),s=new Stack(max);s.setLore([{text:'foreign keepsake'}]);
 f.data.setItemProperty(s,f.api.HOT_UNTIL_KEY,1000);
 f.data.setItemProperty(s,'foreign:metadata','preserve');
 f.data.setItemProperty(s,SEASONING_LIST_KEY,JSON.stringify(['minecraft:gunpowder']));
 writePublicFood(s,{v:1,hotUntil:1000,seasoning:['minecraft:redstone'],nativeVariant:7});
 return {...f,s};
}
for(const max of [64,1])for(const fault of ['before-write','after-write','silent-drop','silent-user-drop'])test('expiry '+max+' restores exact public/private metadata after cold replacement '+fault,async()=>{
 const {api,data,s}=await expiredFixture(max),before=s.getRawLore(),properties=propertySnapshot(data,s),write=s.setLore.bind(s);
 let removed=false,injected=false;
 s.setLore=rows=>{
  const payload=rows.find(row=>row?.translate==='senluo.public.food.v1');
  if(!payload&&readPublicFood(s).present)removed=true;
  if(removed&&!injected&&payload&&JSON.parse(payload.with[0]).hotUntil===0){
   injected=true;if(fault==='before-write')throw Error('cold replacement fault');
   if(fault==='silent-drop'){write(rows.filter(row=>row!==payload));return}
   if(fault==='silent-user-drop'){write(rows.filter(row=>row?.text!=='foreign keepsake'));return}
   write(rows);throw Error('cold replacement applied before fault');
  }
  write(rows);
 };
 api.refreshHotLore(s);assert.equal(removed,true);assert.equal(injected,true);
 assert.deepEqual(s.getRawLore(),before);assert.equal(propertySnapshot(data,s),properties);
 assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:1000,seasoning:['minecraft:redstone'],nativeVariant:7});
 assert.equal(api.isHotFood(s),false);
 api.refreshHotLore(s);assert.equal(api.hotUntil(s),0);assert.equal(data.getItemProperty(s,api.HOT_UNTIL_KEY),undefined);
 assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:0,seasoning:['minecraft:redstone'],nativeVariant:7});
 assert.equal(data.getItemProperty(s,'foreign:metadata'),'preserve');
 assert.equal(data.getItemProperty(s,SEASONING_LIST_KEY),JSON.stringify(['minecraft:gunpowder']));
});
for(const fault of ['throw','silent-drop','after-write'])test('expiry rollback '+fault+' is checked before returning a working copy',async()=>{
 const {api,data,s}=await expiredFixture(),before=s.getRawLore(),properties=propertySnapshot(data,s),write=s.setLore.bind(s);
 let failed=false;
 s.setLore=rows=>{
  const payload=rows.find(row=>row?.translate==='senluo.public.food.v1');
  if(payload&&JSON.parse(payload.with[0]).hotUntil===0){failed=true;throw Error('cold write rejected')}
  if(failed){
   if(fault==='throw')throw Error('rollback rejected');
   if(fault==='silent-drop'){write(rows.filter(row=>row!==payload));return}
   write(rows);throw Error('rollback applied before fault');
  }
  write(rows);
 };
 if(fault==='after-write'){
  api.refreshHotLore(s);assert.deepEqual(s.getRawLore(),before);assert.equal(propertySnapshot(data,s),properties);
 }else assert.throws(()=>api.refreshHotLore(s),/expired heat rollback unverified/);
});
test('a failed native heat restoration still restores raw public lore and rejects the damaged copy',async()=>{
 const {api,data,s}=await expiredFixture(1),before=s.getRawLore(),write=s.setLore.bind(s),setProperty=s.setDynamicProperty.bind(s);
 let failed=false;
 s.setLore=rows=>{
  const payload=rows.find(row=>row?.translate==='senluo.public.food.v1');
  if(payload&&JSON.parse(payload.with[0]).hotUntil===0){failed=true;throw Error('cold replacement fault')}
  write(rows);
 };
 s.setDynamicProperty=(key,value)=>{if(failed&&key===api.HOT_UNTIL_KEY)throw Error('native restoration failed');setProperty(key,value)};
 assert.throws(()=>api.refreshHotLore(s),/expired heat rollback unverified/);
 assert.deepEqual(s.getRawLore(),before);assert.equal(data.getItemProperty(s,api.HOT_UNTIL_KEY),undefined);
 assert.equal(data.getItemProperty(s,SEASONING_LIST_KEY),JSON.stringify(['minecraft:gunpowder']));
 assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:1000,seasoning:['minecraft:redstone'],nativeVariant:7});
});

test('native RawMessage key reordering does not roll successful expiry back into stale heat',async()=>{
 const {api}=await fixture(),s=new Stack(1),write=s.setLore.bind(s);
 s.setLore=rows=>write(rows.map(row=>row&&typeof row==='object'?Object.fromEntries(Object.entries(row).reverse()):row));
 writePublicFood(s,{v:1,hotUntil:1098,seasoning:['minecraft:redstone','minecraft:gunpowder','minecraft:redstone'],nativeVariant:7});
 s.dp.set('test:foreign',77);
 api.refreshHotLore(s);
 assert.deepEqual(readPublicFood(s).state,{v:1,hotUntil:0,seasoning:['minecraft:redstone','minecraft:gunpowder','minecraft:redstone'],nativeVariant:7});
 assert.equal(s.dp.get('test:foreign'),77);assert.equal(api.hotUntil(s),0);
});
