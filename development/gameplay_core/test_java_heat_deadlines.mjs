/** Production metadata modules with storage-operation adapters; no player/client claim. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {bucketHotUntil,readPublicFood,writePublicFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
const oracle=JSON.parse(fs.readFileSync(new URL('./fixtures/java-heat-deadlines.json',import.meta.url)));
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
async function fixture(){
 let tick=1099;const props=new Map(),context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Math,Boolean,Error,Date});
 const world={getAbsoluteTime:()=>tick,getDynamicProperty:k=>props.get(k),setDynamicProperty:(k,v)=>v===undefined?props.delete(k):props.set(k,v)};
 const system={get currentTick(){return tick}};
 const server=new vm.SyntheticModule(['world','system'],function(){this.setExport('world',world);this.setExport('system',system)},{context});
 // Tooltip event scheduling is unrelated to heat writes; its pure lore module is real.
 const tooltipEvents=new vm.SyntheticModule([],function(){},{context});
 const modules=new Map();
 function load(url){const id=url.href;if(!modules.has(id))modules.set(id,new vm.SourceTextModule(fs.readFileSync(url,'utf8'),{context,identifier:id}));return modules.get(id)}
 const adapter=load(new URL('a2750_food_state_adapter.js',root));
 await adapter.link((spec,parent)=>spec==='@minecraft/server'?server:spec==='./a2769_food_tooltip_runtime.js'?tooltipEvents:load(new URL(spec,parent.identifier)));
 await adapter.evaluate();
 const data=modules.get(new URL('itemDataCore.js',root).href).namespace;
 return {api:adapter.namespace,data,setTick:v=>tick=v};
}
class Stack{
 constructor(maxAmount=64){this.typeId='minecraft:cooked_beef';this.maxAmount=maxAmount;this.amount=1;this.lore=[];this.dp=new Map()}
 getRawLore(){return structuredClone(this.lore)}setLore(v){if(v.length>20)throw Error('native lore capacity');this.lore=structuredClone(v)}
 getDynamicProperty(k){return this.dp.get(k)}getDynamicPropertyIds(){return [...this.dp.keys()]}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v);if(this.failOnce){this.failOnce=false;throw Error('post-write property fault')}}
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
