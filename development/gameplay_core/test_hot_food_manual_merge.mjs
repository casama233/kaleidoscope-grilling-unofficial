import {loadHotRuntime} from './load_hot_runtime_vm.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class ItemStack{
 constructor(typeId,amount=1,food=true){this.typeId=typeId;this.amount=amount;this.food=food;this.dp=new Map();this.lore=[];this.nameTag=''}
 get maxAmount(){return 64}
 getComponent(id){return id==='minecraft:food'&&this.food?{}:undefined}
 hasTag(id){return id==='minecraft:is_food'&&this.food}
 getDynamicPropertyIds(){return [...this.dp.keys()]}
 getDynamicProperty(k){return this.dp.get(k)}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getRawLore(){return [...this.lore]}
 getLore(){return [...this.lore]}setLore(v){this.lore=[...v]}
 clone(){const s=new ItemStack(this.typeId,this.amount,this.food);s.dp=new Map(this.dp);s.lore=[...this.lore];s.nameTag=this.nameTag;return s}
}
class Container{
 constructor(size){this.size=size;this.slots=Array(size).fill(undefined)}
 getItem(i){return this.slots[i]}setItem(i,v){this.slots[i]=v}
}
const {hot,data}=await loadHotRuntime();
function heat(stack,remaining){stack.setLore(['§c🔥 test']);data.setItemProperty(stack,'kaleidoscope_grilling:hot_until',1000+remaining);return stack}

const c=new Container(8);
const a=heat(new ItemStack('minecraft:cooked_beef',2,true),1200);
const b=heat(new ItemStack('minecraft:cooked_beef',1,true),600);
const cold=new ItemStack('minecraft:cooked_beef',5,true);
c.setItem(0,a);c.setItem(3,b);c.setItem(5,cold);
let result=hot.compactMatchingHotFood(c,a.clone(),1000);
assert.equal(result.changed,true);assert.equal(result.count,3);assert.equal(result.stacks,1);
assert.equal(c.getItem(0).amount,3);
assert.equal(data.getItemProperty(c.getItem(0),'kaleidoscope_grilling:hot_until')-1000,1000);
assert.equal(c.getItem(5).amount,5);

const third=new Container(4),x=heat(new ItemStack('example:meal',1,true),500),y=heat(new ItemStack('example:meal',2,true),800);
third.setItem(0,x);third.setItem(2,y);result=hot.compactMatchingHotFood(third,x.clone(),1000);
assert.equal(result.changed,true);assert.equal(third.getItem(0).amount,3);
assert.equal(data.getItemProperty(third.getItem(0),'kaleidoscope_grilling:hot_until')-1000,700);

const tools=new Container(3),t1=heat(new ItemStack('example:tool',1,false),500),t2=heat(new ItemStack('example:tool',1,false),500);
tools.setItem(0,t1);tools.setItem(1,t2);
assert.equal(hot.compactMatchingHotFood(tools,t1.clone(),1000).changed,false);
console.log('Generic manual hot-food merge: PASS');

const failing=new Container(4),fa=heat(new ItemStack('minecraft:cooked_beef',2,true),1200),fb=heat(new ItemStack('minecraft:cooked_beef',1,true),600);failing.setItem(0,fa);failing.setItem(2,fb);const write=failing.setItem.bind(failing);let fail=true;failing.setItem=(i,s)=>{if(i===2&&fail){fail=false;throw Error('injected write');}write(i,s);};const rejected=hot.compactMatchingHotFood(failing,fa.clone(),1000);assert.equal(rejected.failed,true);assert.equal(failing.getItem(0).amount,2);assert.equal(failing.getItem(2).amount,1);assert.equal(data.getItemProperty(failing.getItem(0),'kaleidoscope_grilling:hot_until'),2200);console.log('Hot-food failed-write rollback: PASS');
