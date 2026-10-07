/** Production planner, visual retargeter and metadata helpers with API doubles.
 * These checks do not certify Minecraft persistence or rendered tooltips.
 * Run: node --test development/gameplay_core/test_seasoning_ingredient_lore.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const scripts=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const load=name=>import(new URL(name,scripts).href);
const [contract,visuals,items,lore,food]=await Promise.all([
 load('a2743_seasoning_contract_core.js'),load('a2766_special_seasoning_visual_core.js'),
 load('itemDataCore.js'),load('localized_lore_core.js'),load('host_api/food_api_core.js')
]);
const main=fs.readFileSync(new URL('main.js',scripts),'utf8');
function body(name){
 const start=main.indexOf('function '+name+'(');assert.ok(start>=0,name);
 let end=main.indexOf('{',start)+1,depth=1;
 while(depth){const c=main[end++];if(c==='{')depth++;if(c==='}')depth--;}
 return main.slice(start,end);
}
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const|class))/g,'');
function fixture({maxAmount=1,creative=false}={}){
 class Stack{
  constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=maxAmount;this.props={};this.lore=[];this.destroy=[];this.place=[];}
  clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));}
  getRawLore(){return structuredClone(this.lore)}setLore(value){this.lore=structuredClone(value)}
  getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(key){return this.props[key]}
  setDynamicProperty(key,value){if(value===undefined)delete this.props[key];else this.props[key]=value;}
  getCanDestroy(){return this.destroy}setCanDestroy(value){this.destroy=[...value]}
  getCanPlaceOn(){return this.place}setCanPlaceOn(value){this.place=[...value]}
 }
 const records=new Map(),world={getDynamicProperty:key=>records.get(key),setDynamicProperty:(key,value)=>records.set(key,value)};
 items.configureItemDataWorld(world);
 const hands={};
 const ctx=vm.createContext({...contract,...visuals,...items,...lore,...food,world,system:{currentTick:1},console,ItemStack:Stack,
  heldByHand:(_player,hand)=>hands[hand],creative:()=>creative,
  SEASON_USES_KEY:contract.SEASONING_USES_KEY,EMPTY_SEASONING_ID:contract.EMPTY_BOTTLE_ID});
 vm.runInContext(strip(fs.readFileSync(new URL('a2750_food_state_adapter.js',scripts),'utf8')),ctx);
 vm.runInContext(strip(fs.readFileSync(new URL('a2766_special_seasoning_visual_runtime.js',scripts),'utf8')),ctx);
 vm.runInContext('const readSeasonings=readFoodSeasonings;'+['getUses','setUses','planSeasoningBottle'].map(body).join('\n')+';this.api={planSeasoningBottle,readSeasonings,getUses};',ctx);
 function bottle(ingredients,uses=0){
  const s=new Stack(visuals.specialSeasoningVisualId(uses,5));s.nameTag='Kept bottle';s.keepOnDeath=true;s.lockMode='inventory';s.destroy=['minecraft:dirt'];s.place=['minecraft:stone'];
  items.setItemProperty(s,contract.SEASONING_LIST_KEY,JSON.stringify(ingredients));
  items.setItemProperty(s,contract.SEASONING_USES_KEY,uses);items.setItemProperty(s,contract.SEASONING_VARIANT_KEY,5);
  items.setItemProperty(s,'test:unrelated','kept');items.setItemLore(s,lore.seasoningLore(16-uses,ingredients.length));return s;
 }
 return {hands,api:ctx.api,bottle};
}
const ingredientsFor=count=>[...contract.BASE_SEASONINGS,...Array(count-3).fill('minecraft:redstone')];
for(const maxAmount of [1,64])for(const hand of ['main','off'])for(const count of [3,8])for(const [uses,needed] of [[0,1],[0,3],[1,1],[14,1]]){
 test(`${maxAmount===1?'native':'legacy stackable'} ${hand} ${count}/8 ingredients, debit ${needed} from ${16-uses}/16`,()=>{
  const f=fixture({maxAmount}),ingredients=ingredientsFor(count),before=f.bottle(ingredients,uses);f.hands[hand]=before;
  const plan=f.api.planSeasoningBottle({},hand,needed);assert.equal(plan.ok,true);assert.equal(plan.mutate,true);
  assert.deepEqual([...f.api.readSeasonings(plan.next)],ingredients);assert.deepEqual([...plan.ingredients],ingredients);
  assert.deepEqual(items.getItemRawLore(plan.next),lore.seasoningLore(16-uses-needed,count));
  assert.equal(f.api.getUses(plan.next),uses+needed);assert.equal(plan.next.typeId,visuals.specialSeasoningVisualId(uses+needed,5));
  for(const key of ['nameTag','keepOnDeath','lockMode','destroy','place'])assert.deepEqual(plan.next[key],before[key]);
  assert.equal(items.getItemProperty(plan.next,'test:unrelated'),'kept');assert.equal(items.getItemProperty(plan.next,contract.SEASONING_VARIANT_KEY),5);
  assert.deepEqual(items.getItemRawLore(before),lore.seasoningLore(16-uses,count));assert.equal(f.api.getUses(before),uses);
 });
}
for(const hand of ['main','off']){
 test(`${hand} exhausted bottle still becomes empty`,()=>{
  const f=fixture(),ingredients=ingredientsFor(8);f.hands[hand]=f.bottle(ingredients,15);
  const plan=f.api.planSeasoningBottle({},hand,1);assert.equal(plan.ok,true);assert.equal(plan.next.typeId,contract.EMPTY_BOTTLE_ID);assert.equal(plan.uses,16);assert.deepEqual([...plan.ingredients],ingredients);
 });
 test(`${hand} insufficient doses do not mutate the bottle`,()=>{
  const f=fixture(),before=f.bottle(ingredientsFor(3),14);f.hands[hand]=before;
  const plan=f.api.planSeasoningBottle({},hand,3);assert.equal(plan.ok,false);assert.equal(plan.reason,'insufficient');assert.equal(plan.remaining,2);assert.equal(f.api.getUses(before),14);assert.deepEqual(items.getItemRawLore(before),lore.seasoningLore(2,3));
 });
 test(`${hand} creative use retains the exact bottle lore and ingredients`,()=>{
  const f=fixture({creative:true}),ingredients=ingredientsFor(8),before=f.bottle(ingredients,1);f.hands[hand]=before;
  const plan=f.api.planSeasoningBottle({},hand,3);assert.equal(plan.ok,true);assert.equal(plan.mutate,false);assert.deepEqual(plan.next,before);assert.deepEqual([...plan.ingredients],ingredients);
 });
}
