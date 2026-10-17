/** Java sameForManualMerge preserves Seasonings components; storage-operation adapters only. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {loadHotRuntime} from './load_hot_runtime_vm.mjs';
import {writePublicFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
const HOT='kaleidoscope_grilling:hot_until',SEASON='kaleidoscope_grilling:seasonings';
class Stack{
 constructor(id='minecraft:cooked_beef',amount=1){this.typeId=id;this.amount=amount;this.maxAmount=64;this.lore=[];this.dp=new Map();this.nameTag=''}
 getRawLore(){return structuredClone(this.lore)}setLore(v){this.lore=structuredClone(v)}
 getDynamicProperty(k){return this.dp.get(k)}getDynamicPropertyIds(){return [...this.dp.keys()]}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getComponent(k){return k==='minecraft:food'?{}:undefined}
 clone(){const n=new Stack(this.typeId,this.amount);n.lore=this.getRawLore();n.dp=new Map(this.dp);n.nameTag=this.nameTag;return n}
}
class Container{
 constructor(){this.size=4;this.rows=Array(4).fill(undefined)}getItem(i){return this.rows[i]?.clone()}setItem(i,s){this.rows[i]=s?.clone()}
 addItem(s){for(let i=0;i<this.size;i++)if(!this.rows[i]){this.setItem(i,s);return undefined}return s.clone()}
}
async function fixture(a,b,{id,rawA,rawB}={}){
 const {hot,data}=await loadHotRuntime(),left=new Stack(id,2),right=new Stack(id,1),c=new Container();
 data.setItemProperty(left,HOT,2200);data.setItemProperty(right,HOT,2200);
 if(rawA!==undefined||a!==undefined)data.setItemProperty(left,SEASON,rawA??JSON.stringify(a));
 if(rawB!==undefined||b!==undefined)data.setItemProperty(right,SEASON,rawB??JSON.stringify(b));
 c.setItem(0,left);c.setItem(1,right);return {hot,data,c,left,right};
}
for(const [label,a,b] of [
 ['different effects',['minecraft:redstone'],['minecraft:gunpowder']],
 ['different effect strength',['minecraft:redstone'],Array(4).fill('minecraft:redstone')],
 ['different ordered layers',['minecraft:redstone','minecraft:gunpowder'],['minecraft:gunpowder','minecraft:redstone']],
 ['plain versus seasoned',undefined,['minecraft:redstone']]
])test('legacy '+label+' remain separate through manual heat merge',async()=>{
 const {hot,c,left}=await fixture(a,b),before=JSON.stringify(c.rows);
 assert.equal(hot.compactMatchingHotFood(c,left,1000).changed,false);
 assert.equal(JSON.stringify(c.rows),before);
});
test('equal legacy seasoning lists still merge with Java heat buckets and retain payload',async()=>{
 const {hot,data,c,left}=await fixture(['minecraft:redstone'],['minecraft:redstone']);
 data.setItemProperty(c.rows[1],HOT,2299);
 assert.equal(hot.compactMatchingHotFood(c,left,1000).changed,true);
 assert.equal(c.getItem(0).amount,3);assert.equal(c.getItem(1),undefined);
 assert.equal(data.getItemProperty(c.getItem(0),SEASON),'["minecraft:redstone"]');
 assert.equal(hot.hotUntil(c.getItem(0)),2200);
});
test('legacy ingredients remain separate in skewer sorting and new output delivery',async()=>{
 const {hot,data,c,left,right}=await fixture(['minecraft:redstone'],['minecraft:gunpowder'],{id:'kaleidoscope_grilling:grilled_beef_skewer'});
 hot.compactSkewerContainer(c,true,1000);assert.equal(c.getItem(0).amount,2);assert.equal(c.getItem(1).amount,1);
 const delivery=new Container();delivery.setItem(0,left);assert.equal(hot.mergeIntoContainer(delivery,right,1000),undefined);
 assert.equal(delivery.getItem(0).amount,2);assert.equal(delivery.getItem(1).amount,1);
 assert.equal(data.getItemProperty(delivery.getItem(0),SEASON),'["minecraft:redstone"]');
 assert.equal(data.getItemProperty(delivery.getItem(1),SEASON),'["minecraft:gunpowder"]');
});
test('unreadable legacy seasoning bytes do not collapse into the empty-list signature',async()=>{
 const {hot,c,left}=await fixture(undefined,undefined,{rawA:'invalid saved redstone',rawB:'invalid saved gunpowder'}),before=JSON.stringify(c.rows);
 assert.equal(hot.compactMatchingHotFood(c,left,1000).changed,false);assert.equal(JSON.stringify(c.rows),before);
});
test('public and legacy storage representations preserve the same ordered seasoning boundary',async()=>{
 const {hot,c,left}=await fixture(['minecraft:redstone'],['minecraft:gunpowder']);
 c.setItem(1,writePublicFood(new Stack(undefined,1),{v:1,hotUntil:2200,seasoning:['minecraft:gunpowder']}));
 assert.equal(hot.compactMatchingHotFood(c,left,1000).changed,false);assert.equal(c.getItem(1).amount,1);
});

test('same seasoning lists bridge public and legacy representation without losing target data',async()=>{
 const {hot,data,c,left}=await fixture(['minecraft:redstone'],undefined);
 c.setItem(1,writePublicFood(new Stack(),{v:1,hotUntil:2200,seasoning:['minecraft:redstone']}));
 assert.equal(hot.compactMatchingHotFood(c,left,1000).changed,true);
 assert.equal(c.getItem(0).amount,3);assert.equal(c.getItem(1),undefined);
 assert.equal(data.getItemProperty(c.getItem(0),SEASON),'["minecraft:redstone"]');
});

test('late merge slot fault restores all earlier credits and original incoming count',async()=>{
 const {hot,c,left}=await fixture([],[]);c.rows[0].amount=61;c.rows[1].amount=62;
 const incoming=left.clone();incoming.amount=5;const before=JSON.stringify(c.rows),write=c.setItem.bind(c);let once=true;
 c.setItem=(i,s)=>{write(i,s);if(i===1&&once){once=false;throw Error('post-write slot fault')}};
 const remainder=hot.mergeIntoContainer(c,incoming,1000);
 assert.equal(remainder.amount,5);assert.equal(JSON.stringify(c.rows),before);assert.equal(incoming.amount,5);
});
test('native addItem post-credit fault rolls back every slot before returning the full output',async()=>{
 const {hot,c,left}=await fixture([],[]);c.rows[0].amount=63;c.rows[1]=undefined;
 const incoming=left.clone();incoming.amount=4;const before=JSON.stringify(c.rows);
 c.addItem=s=>{c.setItem(1,s);throw Error('native addItem post-credit fault')};
 const remainder=hot.mergeIntoContainer(c,incoming,1000);
 assert.equal(remainder.amount,4);assert.equal(JSON.stringify(c.rows),before);
});
test('strict output delivery propagates the fault after restoring original slots',async()=>{
 const {hot,c,left}=await fixture([],[]);c.rows[0].amount=63;c.rows[1]=undefined;
 const incoming=left.clone();incoming.amount=4;const before=JSON.stringify(c.rows);
 c.addItem=s=>{c.setItem(1,s);throw Error('strict native fault')};
 assert.throws(()=>hot.mergeIntoContainer(c,incoming,1000,true),/strict native fault/);
 assert.equal(JSON.stringify(c.rows),before);
});
test('unresolved rollback throws instead of authorizing a possibly duplicate remainder',async()=>{
 const {hot,c,left}=await fixture([],[]);c.rows[0].amount=63;c.rows[1]=undefined;
 const incoming=left.clone();incoming.amount=4;const write=c.setItem.bind(c);let rollback=false;
 c.addItem=s=>{write(1,s);rollback=true;throw Error('post-credit fault')};
 c.setItem=(i,s)=>{if(rollback)throw Error('unavailable during rollback');write(i,s)};
 assert.throws(()=>hot.mergeIntoContainer(c,incoming,1000),/output delivery unresolved/);
});
