/** Actual runtime bodies + storage-operation doubles. Not Minecraft/client evidence. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as data from '../../projects/grilling/gameplay_core/behavior_pack/scripts/data.js';
import * as logic from '../../projects/grilling/gameplay_core/behavior_pack/scripts/core_logic.js';
import * as skewers from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js';
import * as items from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
import * as snapshots from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
import * as seasoning from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
import * as bottleVisuals from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2766_special_seasoning_visual_core.js';
import * as oil from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2734_cookery_oil_pot_core.js';
import * as portableOil from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/oil_api_core.js';
import * as portableFood from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import {resolveSecretSmokedId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/secret_compat_core.js';
import * as tools from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a275_grill_input_core.js';
import * as heat from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
import {foodFacts} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/food_snapshot_core.js';
import {primitiveStackProps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';
import {commitSteps,commitTwoParty} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {slotWrite} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_transfer_plan.js';
import {captureEatingIdentity,eatingStillCurrent,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url),read=n=>fs.readFileSync(new URL(n,root),'utf8'),source=read('main.js');
function fn(name){const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);let end=source.indexOf('{',start)+1,depth=1;while(depth){const c=source[end++];if(c==='{')depth++;if(c==='}')depth--}return source.slice(start,end)}
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/^export \{[^\n]*\n/gm,'').replace(/\bexport (?=(function|const|class))/g,'');
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.nameTag='';this.lore=[];this.props={};this.damage=0;this.keepOnDeath=false;this.lockMode='none';this.destroy=[];this.place=[]}
 get maxAmount(){return this.typeId.includes('skewer')?1:64}clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}))}
 getRawLore(){return structuredClone(this.lore)}setLore(lore){this.lore=structuredClone(lore)}getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(k){return this.props[k]}setDynamicProperty(k,v){if(v===undefined)delete this.props[k];else this.props[k]=v}
 getCanDestroy(){return this.destroy}getCanPlaceOn(){return this.place}setCanDestroy(v){this.destroy=v}setCanPlaceOn(v){this.place=v}getTags(){return []}
 getComponent(id){if(id==='minecraft:food'&&data.FOOD_DATA[this.typeId])return {nutrition:data.FOOD_DATA[this.typeId].nutrition,saturationModifier:data.FOOD_DATA[this.typeId].saturation};if(id==='minecraft:durability'&&this.typeId==='minecraft:flint_and_steel'){const self=this;return {maxDurability:64,get damage(){return self.damage},set damage(v){self.damage=v}}}}
}
class Container{constructor(size){this.size=size;this.rows=Array(size)}getItem(i){return this.rows[i]?.clone()}setItem(i,s){this.rows[i]=s?.clone()}}
function fixture(){
 let state=logic.initialState(),off,tick=1000,failHand=false;const metadata=new Map(),grill=new Container(3),bag=new Container(12),sounds=[],settlements=[],notices=[];
 const world={getAbsoluteTime:()=>tick,getDynamicProperty:k=>metadata.get(k),setDynamicProperty:(k,v)=>v===undefined?metadata.delete(k):metadata.set(k,v)};items.configureItemDataWorld(world);
 const dimension={playSound(){},spawnItem(){throw Error('unexpected drop')}},block={isValid:true,typeId:data.GRILL_ID,x:0,y:0,z:0,location:{x:0,y:0,z:0},dimension};
 const hunger={currentValue:0,effectiveMax:20,setCurrentValue(v){this.currentValue=v}},saturation={currentValue:0,setCurrentValue(v){this.currentValue=v}};
 const holder={id:'storage-adapter',name:'Storage adapter',selectedSlotIndex:0,isSneaking:false,dimension,location:block.location,playAnimation(){},getComponent:id=>id.endsWith('hunger')?hunger:id.endsWith('saturation')?saturation:undefined};
 const write=(hand,s)=>{if(hand==='off')off=s?.clone();else bag.setItem(0,s);if(failHand){failHand=false;throw Error('injected hand write')}};
 const ctx=vm.createContext({...data,...logic,...skewers,...items,...snapshots,...seasoning,...bottleVisuals,...oil,...tools,...heat,world,system:{get currentTick(){return tick}},ItemStack:Stack,foodFacts,primitiveStackProps,commitSteps,commitTwoParty,slotWrite,captureEatingIdentity,eatingStillCurrent,commitEating,
  console:{warn(){}},COOKERY_FILLED:oil.COOKERY_FILLED_ID,SEASON_USES_KEY:seasoning.SEASONING_USES_KEY,SEASON_VARIANT_KEY:seasoning.SEASONING_VARIANT_KEY,OIL_TOOLS:{},
  ...portableOil,...portableFood,ensureOilHandPublished:()=>true,OIL_TYPES:{canola:{heatTicks:1200},secret_chili:{heatTicks:12000},premium_chili:{heatTicks:24000}},heldMain:()=>bag.getItem(0),heldOff:()=>off,heldByHand:(_,hand)=>hand==='off'?off:bag.getItem(0),creative:()=>false,
  captureWritableHand:(_,hand)=>({before:(hand==='off'?off:bag.getItem(0))?.clone(),write:s=>write(hand,s)}),mainContainer:()=>bag,inv:()=>grill,occupied:()=>grill.rows.filter(Boolean).length,
  readState:()=>structuredClone(state),writeState:(_b,s)=>state=structuredClone(s),resetBlock:(_b,lit)=>state={...logic.initialState(),lit},commitStationTransfer:(_b,steps)=>commitSteps(steps),quarantineStation(){throw Error('quarantine')},
  blockSound:(_b,id)=>sounds.push(id),useSound:(_p,id)=>sounds.push(id),message:(_p,text)=>notices.push(text),awardLookingThePart(){},awardGleamingWithOil(){},
  isCompatRawSkewer:()=>false,customSkewerCookedId:()=>undefined,skewerIngredientDecision:()=>'',resolveSecretSmokedId,
  afterCommitted:(_p,id,meta)=>settlements.push({id,hot:meta.hot,seasonings:meta.seasonings}),RAW_NAUSEA:{},secretRemainders(){},now:()=>tick,
  prepareOutputDelivery:(_p,rows)=>({apply(){if(rows.length)throw Error('unexpected starter remainder')},rollback(){}})
 });
 vm.runInContext(strip(read('a2769_food_tooltip_core.js')),ctx);
 vm.runInContext(strip(read('a2734_cookery_oil_pot_adapter.js')),ctx);
 vm.runInContext(strip(read('a2750_food_state_adapter.js')),ctx);
 vm.runInContext(strip(read('a2766_special_seasoning_visual_runtime.js')),ctx);
 vm.runInContext('const setHot=setHotFood,isHot=isHotFood,setSeasonings=setFoodSeasonings,readSeasonings=readFoodSeasonings;',ctx);
 const names=['copyOne','copyCustomData','reducedStack','planDamagedHand','transactionStatus','commitGrillAndHand','ingredientSnapshot','restoreIngredient','readRowsFromKey','readSkewerRows','isSecretCooked','readEffectiveSkewerRows','rowLabel','writeSkewerRows','setSecretCreator','dynamicFood','isEdible','threadOutcome','threadCurrent','getUses','setUses','heatForOil','planCookeryOil','planSeasoningBottle','cookedIngredientRows','setCookedIngredientRows','cookedStack','failedStack','outputFor','extract','handleGrill','hungerSettle'];
 vm.runInContext(names.map(fn).join('\n')+';this.api={threadCurrent,handleGrill,extract,hungerSettle,readSkewerRows,readEffectiveSkewerRows,isSecretCooked,setSeasonings,buildCookeryOilPot,readCookeryOilPot,getUses,setUses,readSeasonings,isHot};',ctx);
 return {api:ctx.api,holder,block,grill,bag,sounds,settlements,notices,hunger,saturation,get main(){return bag.getItem(0)},set main(s){write('main',s)},get off(){return off},set off(s){write('off',s)},get state(){return state},failNextHand(){failHand=true},tick(n){tick+=n;state=logic.tickState(state,grill.rows.filter(Boolean).length,n).state},handle(){ctx.api.handleGrill(block,holder)},seasoning(){const s=new Stack(data.SEASONING_ID);ctx.api.setSeasonings(s,seasoning.BASE_SEASONINGS);ctx.api.setUses(s,0);return s}};
}
const cooked=skewers.recipeTable().filter(r=>r.cooked);
function thread(f,recipe){f.off=new Stack(skewers.UNFINISHED_ID);for(const slot of recipe.slots){f.main=new Stack(slot[0]);assert.equal(f.api.threadCurrent(f.holder),true);assert.equal(f.main,undefined)}assert.equal(f.off.typeId,recipe.id);return f.off.clone()}
function cook(f,raw,count=1){f.main=new Stack('minecraft:flint_and_steel');f.handle();assert.equal(f.state.lit,true);assert.equal(f.main.damage,1);for(let i=0;i<count;i++){f.main=raw.clone();f.handle()}assert.equal(f.grill.rows.filter(Boolean).length,count);f.main=f.api.buildCookeryOilPot('canola',10);f.handle();assert.equal(f.api.readCookeryOilPot(f.main).count,10-count);assert.equal(f.state.phase,1);f.main=undefined;for(let i=0;i<4;i++){f.handle();if(i<3)f.tick(20)}assert.equal(f.state.phase,2);f.main=f.seasoning();f.handle();assert.equal(f.api.getUses(f.main),count);assert.equal(f.state.seasoned,true);f.main=undefined;assert.equal(f.api.extract(f.block,f.holder,true),count);return f.bag.getItem(0)}
for(const recipe of cooked)test(recipe.id+' threads, cooks, retains heat/seasoning and settles once',()=>{const f=fixture(),raw=thread(f,recipe);f.off=undefined;const output=cook(f,raw);assert.equal(output.typeId,recipe.cooked);assert.equal(f.api.isHot(output),true);assert.deepEqual([...f.api.readSeasonings(output)],[...seasoning.BASE_SEASONINGS]);assert.equal(f.state.phase,0);assert.equal(f.state.lit,true);f.hunger.currentValue=10;f.main=output;const active={hand:'main',use:captureEatingIdentity(output,'main',0),meta:{hot:true,hotUntil:2200,seasonings:[...seasoning.BASE_SEASONINGS]}};assert.equal(f.api.hungerSettle(f.holder,recipe.cooked,active),true);assert.equal(f.main,undefined);assert.equal(f.bag.getItem(0),undefined);assert.equal(f.api.hungerSettle(f.holder,recipe.cooked,active),false);assert.equal(f.settlements.length,1);const facts=data.FOOD_DATA[recipe.cooked];assert.equal(f.hunger.currentValue,Math.min(20,10+facts.nutrition));assert.equal(f.saturation.currentValue,Math.min(f.hunger.currentValue,facts.nutrition*facts.saturation*2*1.25));});
test('three occupied slots cost three oil points and three seasoning uses',()=>{const f=fixture(),raw=thread(f,cooked.find(r=>r.id.endsWith('fish_skewer')));f.off=undefined;cook(f,raw,3);assert.equal(f.bag.rows.filter(Boolean).length,3);assert.equal(f.grill.rows.filter(Boolean).length,0)});
test('insufficient oil/seasoning blocks phase progress and preserves inputs',()=>{const f=fixture(),raw=thread(f,cooked.find(r=>r.id.endsWith('fish_skewer')));f.off=undefined;f.main=new Stack('minecraft:flint_and_steel');f.handle();for(let i=0;i<3;i++){f.main=raw;f.handle()}f.main=f.api.buildCookeryOilPot('canola',2);f.handle();assert.equal(f.state.phase,0);assert.equal(f.api.readCookeryOilPot(f.main).count,2);f.main=f.api.buildCookeryOilPot('canola',3);f.handle();f.main=undefined;for(let i=0;i<4;i++){f.handle();if(i<3)f.tick(20)}const bottle=f.seasoning();f.api.setUses(bottle,14);f.main=bottle;f.handle();assert.equal(f.state.seasoned,false);assert.equal(f.api.getUses(f.main),14)});
test('failed oil hand write rolls both oil and cooking state back without success sound',()=>{const f=fixture(),raw=thread(f,cooked.find(r=>r.id.endsWith('fish_skewer')));f.off=undefined;f.main=new Stack('minecraft:flint_and_steel');f.handle();f.main=raw;f.handle();f.main=f.api.buildCookeryOilPot('canola',3);const before=f.sounds.length;f.failNextHand();f.handle();assert.equal(f.state.phase,0);assert.equal(f.api.readCookeryOilPot(f.main).count,3);assert.equal(f.sounds.length,before)});

test('custom three-food secret skewer cooks ingredient food and creator data before settling',()=>{
 const f=fixture(),recipe={id:skewers.SECRET_ID,slots:[['minecraft:apple'],['minecraft:carrot'],['minecraft:beef']]};
 const raw=thread(f,recipe);assert.equal(JSON.parse(items.getItemProperty(raw,skewers.SECRET_CREATOR_KEY)).id,f.holder.id);f.off=undefined;
 const output=cook(f,raw);assert.equal(f.api.isSecretCooked(output),true);
 assert.deepEqual([...f.api.readEffectiveSkewerRows(output)].map(r=>r.id),['minecraft:apple','minecraft:carrot','minecraft:cooked_beef']);
 f.main=output;const active={hand:'main',use:captureEatingIdentity(output,'main',0),meta:{hot:true,hotUntil:2200,seasonings:[...seasoning.BASE_SEASONINGS]}};
 assert.equal(f.api.hungerSettle(f.holder,skewers.SECRET_ID,active),true);assert.equal(f.main,undefined);assert.equal(f.hunger.currentValue,9);assert.equal(f.settlements.length,1);
});
test('ordinary configured skewer threads but cannot enter the raw cooking pipeline',()=>{
 const f=fixture(),recipe=skewers.recipeTable().find(r=>!r.cooked),raw=thread(f,recipe);f.off=undefined;
 f.main=new Stack('minecraft:flint_and_steel');f.handle();f.main=raw;f.handle();
 assert.equal(f.grill.rows.filter(Boolean).length,0);assert.equal(f.main.typeId,recipe.id);assert.equal(f.state.phase,0);
});
