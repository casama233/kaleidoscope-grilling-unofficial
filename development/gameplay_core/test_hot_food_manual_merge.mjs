import {loadHotRuntime} from './load_hot_runtime_vm.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {SECRET_CREATOR_KEY} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js';
import {creatorLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';

class ItemStack{
 constructor(typeId,amount=1,food=true){this.typeId=typeId;this.amount=amount;this.food=food;this.dp=new Map();this.lore=[];this.nameTag=''}
 get maxAmount(){return 64}
 getComponent(id){return id==='minecraft:food'&&this.food?{}:undefined}
 hasTag(id){return id==='minecraft:is_food'&&this.food}
 getDynamicPropertyIds(){return [...this.dp.keys()]}
 getDynamicProperty(k){return this.dp.get(k)}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getRawLore(){return [...this.lore]}
 getLore(){return [...this.lore]}setLore(v){if(v.length>20)throw Error('native lore capacity');this.lore=[...v]}
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

const keepsake={rawtext:[{text:'§c🔥 '},{translate:'example:keepsake'}]},translated=new Container(2);
const tr1=heat(new ItemStack('minecraft:cooked_beef',1,true),600),tr2=heat(new ItemStack('minecraft:cooked_beef',1,true),600);
for(const stack of [tr1,tr2])stack.setLore([keepsake,...stack.getRawLore()]);
translated.setItem(0,tr1);translated.setItem(1,tr2);
assert.equal(hot.compactMatchingHotFood(translated,tr1.clone(),1000).changed,true);
assert.deepEqual(translated.getItem(0).getRawLore()[0],keepsake);
assert.equal(translated.getItem(0).getRawLore()[1].rawtext[1].translate,'tooltip.kaleidoscope_grilling.smoky_warmth');
console.log('Raw translated foreign lore survives heat refresh and merge: PASS');

const failing=new Container(4),fa=heat(new ItemStack('minecraft:cooked_beef',2,true),1200),fb=heat(new ItemStack('minecraft:cooked_beef',1,true),600);failing.setItem(0,fa);failing.setItem(2,fb);const write=failing.setItem.bind(failing);let fail=true;failing.setItem=(i,s)=>{if(i===2&&fail){fail=false;throw Error('injected write');}write(i,s);};const rejected=hot.compactMatchingHotFood(failing,fa.clone(),1000);assert.equal(rejected.failed,true);assert.equal(failing.getItem(0).amount,2);assert.equal(failing.getItem(2).amount,1);assert.equal(data.getItemProperty(failing.getItem(0),'kaleidoscope_grilling:hot_until'),2200);console.log('Hot-food failed-write rollback: PASS');

const {writePublicFood}=await import('../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js');
const distinct=new Container(2),first=writePublicFood(new ItemStack('minecraft:cooked_beef'),{v:1,hotUntil:2200,seasoning:['minecraft:redstone']}),second=writePublicFood(new ItemStack('minecraft:cooked_beef'),{v:1,hotUntil:2200,seasoning:['minecraft:gunpowder']});
distinct.setItem(0,first);distinct.setItem(1,second);assert.equal(hot.compactMatchingHotFood(distinct,first.clone(),1000).changed,false);assert.equal(distinct.getItem(0).amount,1);assert.equal(distinct.getItem(1).amount,1);
console.log('Public seasonings prevent an incompatible heat merge: PASS');

const variants=new Container(2),v1=writePublicFood(new ItemStack('example:meal'),{v:1,hotUntil:2237,seasoning:[],nativeVariant:1}),v2=writePublicFood(new ItemStack('example:meal'),{v:1,hotUntil:2237,seasoning:[],nativeVariant:2});
variants.setItem(0,v1);variants.setItem(1,v2);assert.equal(hot.compactMatchingHotFood(variants,v1.clone(),1000).changed,false);
const precise=new Container(2),pa=heat(new ItemStack('minecraft:cooked_beef'),1277),pb=heat(new ItemStack('minecraft:cooked_beef'),1299);assert.equal(data.getItemProperty(pa,'kaleidoscope_grilling:hot_until'),2277);assert.equal(data.getItemProperty(pb,'kaleidoscope_grilling:hot_until'),2299);precise.setItem(0,pa);precise.setItem(1,pb);assert.equal(hot.compactMatchingHotFood(precise,pa.clone(),1000).changed,true);assert.equal(data.getItemProperty(precise.getItem(0),'kaleidoscope_grilling:hot_until'),2200);
console.log('Java bucketed heat merge, preserved legacy inputs and native variant boundaries: PASS');

for(const now of [1000,1099,1150])for(const portable of [false,true]){
 const target=heat(new ItemStack('minecraft:cooked_beef',62),1277),source=heat(new ItemStack('minecraft:cooked_beef',5),1499),partial=new Container(1);
 if(portable)for(const stack of [target,source])writePublicFood(stack,{v:1,hotUntil:data.getItemProperty(stack,'kaleidoscope_grilling:hot_until'),seasoning:['minecraft:redstone'],nativeVariant:7});
 const originalLore=source.getRawLore(),originalHeat=hot.hotUntil(source);partial.setItem(0,target);
 partial.addItem=remaining=>remaining;
 const remainder=hot.mergeIntoContainer(partial,source,now);
 const weighted=Math.floor(((2277-now)*62+(2499-now)*2)/64),expected=Math.floor((now+weighted)/100)*100;
 assert.equal(partial.getItem(0).amount,64);assert.equal(hot.hotUntil(partial.getItem(0)),expected);
 assert.equal(remainder.amount,3);assert.equal(hot.hotUntil(remainder),originalHeat);assert.deepEqual(remainder.getRawLore(),originalLore);
 assert.equal(source.amount,5);assert.equal(hot.hotUntil(source),2499);assert.deepEqual(source.getRawLore(),originalLore);
}
console.log('Partial heat merges bucket only the weighted target and preserve exact source remainder metadata/count: PASS');

for(const portable of [false,true]){
 const cap=portable?18:19,target=new ItemStack('minecraft:cooked_beef',62),source=new ItemStack('minecraft:cooked_beef',5),user=Array.from({length:cap},(_,i)=>({text:'keepsake '+i})),partial=new Container(1);
 for(const [stack,until] of [[target,2277],[source,2499]]){
  stack.setLore(user);data.setItemProperty(stack,'kaleidoscope_grilling:hot_until',until);
  if(portable)writePublicFood(stack,{v:1,hotUntil:until,seasoning:['minecraft:redstone'],nativeVariant:7});
 }
 const before=source.getRawLore();partial.setItem(0,target);partial.addItem=remaining=>remaining;
 const remainder=hot.mergeIntoContainer(partial,source,1150);
 assert.equal(target.amount,64);assert.equal(hot.hotUntil(target),2200);assert.equal(target.getRawLore().length,20);assert.deepEqual(target.getRawLore().slice(0,cap),user);
 assert.equal(remainder.amount,3);assert.equal(hot.hotUntil(remainder),2499);assert.deepEqual(remainder.getRawLore(),before);
}
console.log('Partial merges retain full private/public carriers without a cosmetic lore overflow: PASS');

// Use the actual creator writer so this test follows the canonical property
// and automatically generated RawMessage, rather than an unused alias key.
const main=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const creatorBegin=main.indexOf('function setSecretCreator('),creatorEnd=main.indexOf('\nfunction ',creatorBegin+1);
const creatorContext=vm.createContext({...data,SECRET_CREATOR_KEY,creatorLore});
vm.runInContext(main.slice(creatorBegin,creatorEnd),creatorContext);
function secret(name,amount){
 const stack=heat(new ItemStack('kaleidoscope_grilling:secret_skewer',amount),1200);
 data.setItemProperty(stack,'kaleidoscope_grilling:skewer_ingredients','same ingredient payload');
 data.setItemLore(stack,[{text:'shared keepsake'},...data.getItemRawLore(stack)]);
 return creatorContext.setSecretCreator(stack,{name,id:'player:'+name});
}
const alice=secret('Alice',62),bob=secret('Bob',5),secretBag=new Container(1);
assert.equal(hot.sameForHeatMerge(alice,bob),true);
secretBag.setItem(0,alice);secretBag.addItem=stack=>stack;
const aliceCreator=data.getItemProperty(alice,SECRET_CREATOR_KEY),bobLore=bob.getRawLore();
const bobRemainder=hot.mergeIntoContainer(secretBag,bob,1000);
assert.equal(secretBag.getItem(0).amount,64);assert.equal(bobRemainder.amount,3);
assert.equal(data.getItemProperty(secretBag.getItem(0),SECRET_CREATOR_KEY),aliceCreator);
assert.ok(data.getItemRawLore(secretBag.getItem(0)).some(line=>JSON.stringify(line)===JSON.stringify(creatorLore('Alice'))));
assert.equal(data.getItemProperty(bobRemainder,SECRET_CREATOR_KEY),data.getItemProperty(bob,SECRET_CREATOR_KEY));
assert.deepEqual(bobRemainder.getRawLore(),bobLore);
for(const change of [
 stack=>{stack.nameTag='custom named serving'},
 stack=>data.setItemLore(stack,[...data.getItemRawLore(stack),creatorLore('A foreign author')]),
 stack=>data.setItemProperty(stack,'kaleidoscope_grilling:creator','foreign metadata'),
 stack=>data.setItemProperty(stack,'kaleidoscope_grilling:skewer_ingredients','different ingredients'),
 stack=>data.setItemProperty(stack,SECRET_CREATOR_KEY,'malformed creator')
]){const changed=secret('Bob',1);change(changed);assert.equal(hot.sameForHeatMerge(alice,changed),false)}
console.log('Canonical secret creators merge while target authors, exact remainders and foreign metadata are retained: PASS');

for(const asMessage of [false,true]){
 const legacy=secret('Carol',1),literal='§7製作者: Carol';
 const lore=data.getItemRawLore(legacy).filter(line=>line?.translate!=='tooltip.kaleidoscope_grilling.creator');
 data.setItemLore(legacy,[...lore,asMessage?{text:literal}:literal]);
 const before=legacy.getRawLore();
 assert.equal(hot.sameForHeatMerge(alice,legacy),true);
 assert.deepEqual(legacy.getRawLore(),before);
 const cleaned=hot.withoutAutomaticCreatorLore(legacy);
 assert.ok(!cleaned.some(line=>line===literal||line?.text===literal));
 assert.deepEqual(legacy.getRawLore(),before);
}
const mixed=secret('Bob',1);data.setItemLore(mixed,[...data.getItemRawLore(mixed),{text:'§7製作者: Bob'}]);
assert.equal(hot.sameForHeatMerge(alice,mixed),true);
const template=secret('Alice',1),foreign=['§7製作者: Alice — keepsake',{text:'§7製作者: Someone else'},creatorLore('Original recipe note')];
data.setItemLore(template,[...data.getItemRawLore(template),...foreign]);
const beforeTemplate=template.getRawLore(),oldCreator=data.getItemProperty(template,SECRET_CREATOR_KEY);
const replacementLore=hot.withoutAutomaticCreatorLore(template);
assert.deepEqual(template.getRawLore(),beforeTemplate);assert.equal(data.getItemProperty(template,SECRET_CREATOR_KEY),oldCreator);
data.setItemProperty(template,SECRET_CREATOR_KEY,JSON.stringify({name:'Bob',id:'player:Bob'}));
data.setItemLore(template,[...replacementLore,creatorLore('Bob')]);
const replacedLore=data.getItemRawLore(template);
assert.ok(!replacedLore.some(line=>JSON.stringify(line)===JSON.stringify(creatorLore('Alice'))));
assert.equal(replacedLore.filter(line=>JSON.stringify(line)===JSON.stringify(creatorLore('Bob'))).length,1);
for(const line of foreign)assert.ok(replacedLore.some(actual=>JSON.stringify(actual)===JSON.stringify(line)));
assert.equal(hot.sameForHeatMerge(template,secret('Bob',1)),false);
console.log('Recipe-book legacy author lines and pre-replacement cleanup retain unrelated creator-like lore: PASS');
