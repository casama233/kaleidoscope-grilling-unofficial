import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {
 DEFAULT_SMOKING_RESULTS,resetParityRegistrationsForTest,registerSmokingResult,resolveSmokingResult,
 registerIngredientFinishBehavior,ingredientFinishBehavior,applyParityRegistration
} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a288_parity_contract.js';
import {ingredientBehavior,rolledIngredientEffects} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_ingredient_effects.js';

let checks=0;const check=(name,fn)=>{fn();checks++;console.log('PASS',name)};

resetParityRegistrationsForTest();
check('vanilla smoking fallback stays available',()=>assert.equal(resolveSmokingResult('minecraft:beef'),'minecraft:cooked_beef'));
check('all built-in smoking ids are valid',()=>{for(const [a,b] of Object.entries(DEFAULT_SMOKING_RESULTS)){assert.match(a,/^[a-z0-9_.-]+:[a-z0-9_./-]+$/);assert.match(b,/^[a-z0-9_.-]+:[a-z0-9_./-]+$/)}});
check('cooperating add-on can register smoking output',()=>{assert.equal(registerSmokingResult('example:raw_kebab','example:smoked_kebab'),true);assert.equal(resolveSmokingResult('example:raw_kebab'),'example:smoked_kebab')});
check('bad smoking registration is rejected',()=>assert.equal(registerSmokingResult('bad id','example:food'),false));

check('cooperating add-on can register finish-use behavior',()=>{
 assert.equal(registerIngredientFinishBehavior('example:spicy_food',{
  effects:[{kind:'native',effect:'speed',ticks:200,amplifier:1,chance:.5}],
  convertTo:'example:bowl',clearPoison:true
 }),true);
 const b=ingredientBehavior({id:'example:spicy_food',edible:true,nutrition:4});
 assert.equal(b.convertTo,'example:bowl');assert.equal(b.clearPoison,true);assert.equal(b.effects[0].effect,'speed');
 assert.equal(rolledIngredientEffects({id:'example:spicy_food',edible:true,nutrition:4},()=>.4).effects.length,1);
 assert.equal(rolledIngredientEffects({id:'example:spicy_food',edible:true,nutrition:4},()=>.6).effects.length,0);
});
check('replaceEffects can override built-in finish effects',()=>{
 assert.equal(applyParityRegistration('food_finish',{item:'minecraft:golden_apple',replaceEffects:true,effects:[{effect:'resistance',ticks:40}]}),true);
 assert.deepEqual(ingredientBehavior({id:'minecraft:golden_apple',edible:true,nutrition:4}).effects.map(x=>x.effect),['resistance']);
});
check('finish behavior snapshots are not mutable registry references',()=>{
 const a=ingredientFinishBehavior('example:spicy_food');a.effects[0].ticks=1;
 assert.equal(ingredientFinishBehavior('example:spicy_food').effects[0].ticks,200);
});

// Runtime hot-food compaction uses the Java FoodState.mergeHot compatibility rule:
// same components + same hot state, without the refrigerator five-minute window.
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=64;this.dp=new Map();this.lore=[];this.nameTag=''}
 clone(){const s=new Stack(this.typeId,this.amount);s.dp=new Map(this.dp);s.lore=[...this.lore];s.nameTag=this.nameTag;return s}
 getDynamicPropertyIds(){return [...this.dp.keys()]}
 getDynamicProperty(k){return this.dp.get(k)}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getLore(){return [...this.lore]}setLore(v){this.lore=[...v]}
}
class Container{
 constructor(size){this.size=size;this.slots=Array(size)}
 getItem(i){return this.slots[i]}setItem(i,v){this.slots[i]=v}
 addItem(stack){const i=this.slots.findIndex(x=>!x);if(i<0)return stack;this.slots[i]=stack;return undefined}
}
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Math,Error});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const merge=new vm.SourceTextModule(fs.readFileSync(new URL('a23_hot_merge.js',root),'utf8'),{context,identifier:'a23_hot_merge.js'});
const hot=new vm.SourceTextModule(fs.readFileSync(new URL('a23_hot_runtime.js',root),'utf8'),{context,identifier:'a23_hot_runtime.js'});
const world=new vm.SyntheticModule(['world'],function(){this.setExport('world',{getAbsoluteTime:()=>1000})},{context,identifier:'@minecraft/server'});
await merge.link(()=>{throw Error('unexpected import')});await merge.evaluate();
await hot.link(async spec=>spec==='@minecraft/server'?world:merge);await world.evaluate();await hot.evaluate();

check('manual hot merge supports non-skewer food and ignores five-minute window',()=>{
 const c=new Container(4),a=new Stack('minecraft:cooked_beef',2),b=new Stack('minecraft:cooked_beef',1);
 a.setDynamicProperty('kaleidoscope_grilling:hot_until',10000);b.setDynamicProperty('kaleidoscope_grilling:hot_until',2000);
 a.setLore(['§c🔥 7:30']);b.setLore(['§c🔥 0:50']);c.setItem(0,a);c.setItem(2,b);
 const result=hot.namespace.compactHotFoodContainer(c,1000,'minecraft:cooked_beef');
 assert.equal(result.changed,true);assert.equal(c.getItem(0).amount,3);
 assert.equal(c.getItem(0).getDynamicProperty('kaleidoscope_grilling:hot_until')-1000,6300);
});
check('manual hot merge preserves component boundaries',()=>{
 const c=new Container(4),a=new Stack('minecraft:cooked_beef',1),b=new Stack('minecraft:cooked_beef',1);
 a.setDynamicProperty('kaleidoscope_grilling:hot_until',3000);b.setDynamicProperty('kaleidoscope_grilling:hot_until',3000);
 a.setDynamicProperty('example:variant','a');b.setDynamicProperty('example:variant','b');c.setItem(0,a);c.setItem(1,b);
 const result=hot.namespace.compactHotFoodContainer(c,1000,'minecraft:cooked_beef');
 assert.equal(result.groups,2);assert.equal(c.getItem(0).amount,1);assert.equal(c.getItem(1).amount,1);
});

console.log(JSON.stringify({passed:checks,failed:0,scope:'A2.8.8 parity contracts + generic manual hot-food merge; no claim of automatic third-party recipe discovery'}));
