/** Production preparation/copy functions with stable ItemStack API doubles. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {canonicalFoodId,eatingItemId,RANDOM_EATING_IDS,isAlternateEatingId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
import {eatingIdentity} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {configureItemDataWorld,setItemLore,setItemProperty} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/itemDataCore.js';
const records=new Map();configureItemDataWorld({getDynamicProperty:key=>records.get(key),setDynamicProperty:(key,value)=>records.set(key,value)});
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_item_runtime.js',import.meta.url),'utf8');
class Stack{
 constructor(typeId,amount=1){Object.assign(this,{typeId,amount,maxAmount:64,nameTag:'',lore:[],props:{},keepOnDeath:false,lockMode:'none',destroy:[],place:[],damage:0,enchantments:[]});}
 clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));}
 getRawLore(){return structuredClone(this.lore)}getLore(){return this.lore.filter(row=>typeof row==='string')}setLore(value){this.lore=structuredClone(value)}
 getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(key){return this.props[key]}setDynamicProperty(key,value){value===undefined?delete this.props[key]:this.props[key]=value}
 getCanDestroy(){return [...this.destroy]}getCanPlaceOn(){return [...this.place]}setCanDestroy(value){this.destroy=[...value]}setCanPlaceOn(value){this.place=[...value]}
 getComponent(id){const self=this;if(id==='minecraft:durability')return {get damage(){return self.damage},set damage(value){self.damage=value}};
  if(id==='minecraft:enchantable')return {getEnchantments:()=>self.enchantments,removeAllEnchantments:()=>self.enchantments=[],addEnchantments:rows=>self.enchantments=rows};}
}
class EnchantmentType{constructor(id){this.id=id}}
function serving(id){
 const stack=new Stack(id,17);stack.nameTag='Original named serving';stack.keepOnDeath=true;stack.lockMode='slot';stack.destroy=['minecraft:stone'];stack.place=['minecraft:dirt'];stack.damage=7;stack.enchantments=[{type:{id:'unbreaking'},level:3}];
 setItemLore(stack,[{translate:'test:foreign_lore',with:['kept']},{rawtext:[{text:'foreign '},{translate:'test:detail'}]}]);
 for(const [key,value] of Object.entries({'test:text':'kept','test:false':false,'test:zero':0,'test:vector':{x:1,y:2,z:3},'kaleidoscope_grilling:hot_until':400,'kaleidoscope_grilling:skewer_ingredients':JSON.stringify([{id:'minecraft:apple'},{id:'minecraft:carrot'},{id:'minecraft:beef'}])}))setItemProperty(stack,key,value);
 return stack;
}
function fixture({main,off,random=.9,failure}={}){
 const state={main:main?.clone(),off:off?.clone()},writes=[],player={id:'prepared-holder',selectedSlotIndex:3};let draws=0,reject=failure;
 const math=Object.create(Math);math.random=()=>{draws++;return random};
 const ctx=vm.createContext({Math:math,ItemStack:Stack,EnchantmentType,canonicalFoodId,eatingItemId,RANDOM_EATING_IDS,isAlternateEatingId,captureSkewerMetadata,restoreSkewerMetadata,metadataSignature,eatingIdentity,
  getHand:(_player,hand)=>state[hand]?.clone(),setHand:(_player,hand,stack)=>{writes.push(hand);state[hand]=stack?.clone();if(reject==='throw'){reject=undefined;throw Error('injected write failure')}if(reject==='silent'){reject=undefined;state[hand].nameTag='lost metadata'}}});
 vm.runInContext(source.replace(/^import .*;\s*$/gm,'').replace(/\bexport /g,'')+'\nthis.api={prepareEatingItems,forgetEatingItem,selectedEatingProfile,copyEatingVariant};',ctx);
 return {api:ctx.api,state,writes,player,get draws(){return draws}};
}
for(const base of RANDOM_EATING_IDS)for(const alternate of [false,true])test(`actual copy preserves every exposed field and total amount: ${base} alternate=${alternate}`,()=>{
 const id=eatingItemId(base,!alternate),original=serving(id),before=captureSkewerMetadata(original),f=fixture({});
 const target=eatingItemId(base,alternate),out=f.api.copyEatingVariant(original,target),expected={...before,id:target};
 assert.equal(out.amount,17);assert.equal(metadataSignature(captureSkewerMetadata(out)),metadataSignature(expected));assert.equal(metadataSignature(captureSkewerMetadata(original)),metadataSignature(before));
 assert.equal(f.api.selectedEatingProfile('THREE_RANDOM',out.typeId),alternate?'THREE_ALT':'THREE');
});
for(const hand of ['main','off'])for(const random of [.1,.9])test(`preparation changes only the captured ${hand} before use and caches its identity: random=${random}`,()=>{
 const base='kaleidoscope_grilling:grilled_gluten_skewer',other=serving('minecraft:apple'),original=serving(eatingItemId(base,random<.5));
 const f=fixture({[hand]:original,[hand==='main'?'off':'main']:other,random}),opposite=hand==='main'?'off':'main';
 f.api.prepareEatingItems(f.player,true);assert.equal(f.draws,0);assert.deepEqual(f.state[hand],original);
 f.api.prepareEatingItems(f.player,false);assert.deepEqual(f.writes,[hand]);assert.deepEqual(f.state[opposite],other);assert.equal(f.state[hand].amount,original.amount);
 assert.equal(f.state[hand].typeId,eatingItemId(base,random>=.5));const expected={...captureSkewerMetadata(original),id:f.state[hand].typeId};assert.equal(metadataSignature(captureSkewerMetadata(f.state[hand])),metadataSignature(expected));
 f.api.prepareEatingItems(f.player,false);assert.equal(f.draws,1);assert.deepEqual(f.writes,[hand]);
 f.api.prepareEatingItems(f.player,true);assert.equal(f.draws,1);
 f.api.forgetEatingItem(f.player.id);f.api.prepareEatingItems(f.player,false);assert.equal(f.draws,2);assert.deepEqual(f.writes,[hand]);
});
for(const hand of ['main','off'])for(const failure of ['throw','silent'])test(`preparation restores ${hand} after ${failure} write failure without touching the other hand`,()=>{
 const original=serving('kaleidoscope_grilling:secret_skewer'),opposite=hand==='main'?'off':'main',other=serving('minecraft:torch'),f=fixture({[hand]:original,[opposite]:other,failure});
 assert.throws(()=>f.api.prepareEatingItems(f.player,false),failure==='throw'?/injected write failure/:/hand write failed/);assert.deepEqual(f.state[hand],original);assert.deepEqual(f.state[opposite],other);assert.deepEqual(f.writes,[hand,hand]);
 f.api.prepareEatingItems(f.player,false);assert.equal(f.state[hand].typeId,eatingItemId(original.typeId,true));assert.equal(f.state[hand].amount,17);
});
test('preparation handles both independent hands and creates no item in an empty hand',()=>{
 const f=fixture({main:serving('kaleidoscope_grilling:ordinary_skewer'),off:serving('kaleidoscope_grilling:secret_skewer')});f.api.prepareEatingItems(f.player,false);assert.deepEqual(f.writes,['main','off']);assert.equal(f.state.main.typeId,eatingItemId('kaleidoscope_grilling:ordinary_skewer',true));assert.equal(f.state.off.typeId,eatingItemId('kaleidoscope_grilling:secret_skewer',true));
 const empty=fixture({off:serving('kaleidoscope_grilling:secret_skewer')});empty.api.prepareEatingItems(empty.player,false);assert.equal(empty.state.main,undefined);assert.deepEqual(empty.writes,['off']);
});
for(const hand of ['main','off'])test(`preparation rechecks a changed serving while preserving ${hand} slot ownership`,()=>{
 const f=fixture({[hand]:serving('kaleidoscope_grilling:grilled_gluten_skewer')});f.api.prepareEatingItems(f.player,false);assert.equal(f.draws,1);
 f.state[hand].amount--;f.api.prepareEatingItems(f.player,false);assert.equal(f.draws,2);assert.equal(f.state[hand].amount,16);
 f.player.selectedSlotIndex++;f.api.prepareEatingItems(f.player,false);assert.equal(f.draws,hand==='main'?3:2);
 f.state[hand]=serving('minecraft:apple');f.api.prepareEatingItems(f.player,false);assert.equal(f.state[hand].typeId,'minecraft:apple');assert.equal(f.state[hand].amount,17);
});
