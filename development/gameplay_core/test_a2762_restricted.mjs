/** Canonical phase-aware bodies; doubles do not certify Bedrock rendering/persistence.
 * Run: node --test development/gameplay_core/test_a2762_restricted.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';
import * as two from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a288_intent_core.js';
const source=n=>fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/'+n,import.meta.url),'utf8');
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'').replace(/^export \{[^}]*\};/gm,'');
function fixture(){
 const phase={restricted:true,destroy:0,place:0,clones:0};
 class Stack{
  constructor(id,meta={}){Object.assign(this,{typeId:id,amount:1,maxAmount:1,nameTag:'',keepOnDeath:false,lockMode:'none',lore:[],props:{},damage:0,destroy:[],place:[]},structuredClone(meta));}
  clone(){phase.clones++;const copy=new Stack(this.typeId);Object.assign(copy,structuredClone({...this}));return copy;}
  getCanDestroy(){phase.destroy++;if(phase.restricted)throw new ReferenceError('getCanDestroy cannot be used in restricted execution');if(this.unreadable)throw Error('unavailable');return [...this.destroy];}
  getCanPlaceOn(){phase.place++;if(phase.restricted)throw new ReferenceError('getCanPlaceOn cannot be used in restricted execution');return [...this.place];}
  getRawLore(){return this.lore.map(text=>({text}));}
  getDynamicPropertyIds(){return Object.keys(this.props);}
  getDynamicProperty(k){return structuredClone(this.props[k]);}
  getComponent(k){return k==='minecraft:durability'?{damage:this.damage}:undefined;}
 }
 const slots=Array(9);let off;
 const container={size:9,getItem:i=>slots[i]?.clone(),setItem(i,s){slots[i]=s?.clone();}};
 const equipment={getEquipment(slot){assert.equal(slot,'offhand');return off?.clone();},setEquipment(slot,s){assert.equal(slot,'offhand');off=s?.clone();return true;}};
 const player={isValid:true,selectedSlotIndex:0,dimension:{id:'minecraft:overworld'},isSneaking:false,getComponent:n=>n==='minecraft:inventory'?{container}:n==='minecraft:equippable'?equipment:undefined};
 const context=vm.createContext({...core,...two,EquipmentSlot:{Offhand:'offhand'},GameMode:{Creative:'creative'}});
 vm.runInContext(strip(source('a2735_player_io.js')),context);vm.runInContext(strip(source('a2762_interaction_intent_adapter.js')),context);
 const api=vm.runInContext('({captureInteractionIntent,interactionIntentStillCurrent,captureTwoHandIntent,twoHandIntentStillCurrent})',context);
 return {phase,Stack,player,api,container,equipment,set(main,other){container.setItem(0,main);equipment.setEquipment('offhand',other);},before(){phase.restricted=true;phase.destroy=phase.place=0;},after(){assert.equal(phase.destroy,0,'before canDestroy calls');assert.equal(phase.place,0,'before canPlaceOn calls');phase.restricted=false;}};
}
const N='kaleidoscope_grilling:';
for(const id of [N+'pending_seasoning',N+'empty_seasoning_bottle','tavern:vodka_q4',N+'sweet_potato'])for(const hand of ['main','off'])test(`restricted ${id} ${hand}: immediate hand and normal deferred action survive`,()=>{
 const f=fixture(),s=new f.Stack(id,{nameTag:'original',lore:['lore'],props:{vector:{x:1,y:2,z:3},flag:true},destroy:['minecraft:dirt'],place:['minecraft:stone']}),other=new f.Stack('x:other');
 f.set(hand==='main'?s:other,hand==='off'?s:other);f.before();const intent=f.api.captureInteractionIntent(f.player,s.clone());assert.equal(intent.hand,hand);assert.ok(f.phase.clones>0);assert.equal(f.api.captureInteractionIntent(f.player,s.clone()).hand,hand);f.after();assert.equal(f.api.interactionIntentStillCurrent(f.player,intent),true);assert.ok(f.phase.destroy>0);assert.ok(f.phase.place>0);
});
test('restricted getters really throw, including on native clones',()=>{const f=fixture(),s=new f.Stack('x:item');assert.throws(()=>s.getCanDestroy(),ReferenceError);assert.throws(()=>s.clone().getCanPlaceOn(),ReferenceError);});
test('single occupied hand remains usable',()=>{const f=fixture(),s=new f.Stack(N+'pending_seasoning');f.set(s);f.before();const i=f.api.captureInteractionIntent(f.player,s.clone());f.after();assert.equal(f.api.interactionIntentStillCurrent(f.player,i),true);});
for(const field of ['destroy','place'])test(`restriction-only off ${field} rejects without reassigning hand`,()=>{
 const f=fixture(),main=new f.Stack(N+'pending_seasoning'),off=new f.Stack(N+'pending_seasoning',{[field]:['minecraft:dirt']});f.set(main,off);f.before();const i=f.api.captureInteractionIntent(f.player,off.clone());assert.equal(i.hand,'main');f.after();assert.equal(f.api.interactionIntentStillCurrent(f.player,i),false);assert.equal(i.hand,'main');const m=f.api.captureInteractionIntent(f.player,main.clone());assert.equal(f.api.interactionIntentStillCurrent(f.player,m),true);
});
for(const field of ['destroy','place','keepOnDeath','lockMode','props','lore','nameTag','damage'])for(const hand of ['main','off'])test(`${hand} ${field} mutation invalidates ordinary and two-hand intent`,()=>{
 const f=fixture(),main=new f.Stack(N+'pending_seasoning'),off=new f.Stack('x:other');f.set(main,off);f.before();const i=f.api.captureInteractionIntent(f.player,main.clone()),both=f.api.captureTwoHandIntent(f.player);assert.ok(both);f.after();assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),true);
 const values={destroy:['minecraft:dirt'],place:['minecraft:stone'],keepOnDeath:true,lockMode:'inventory',props:{new:true},lore:['new'],nameTag:'new',damage:1},changed=(hand==='main'?main:off).clone();changed[field]=values[field];if(hand==='main')f.container.setItem(0,changed);else f.equipment.setEquipment('offhand',changed);assert.equal(f.api.interactionIntentStillCurrent(f.player,i),false);assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),false);
});
test('native clones freeze source mutations; changed stored restrictions invalidate',()=>{
 const f=fixture(),main=new f.Stack('x:main'),off=new f.Stack('x:off');f.set(main,off);f.before();const i=f.api.captureInteractionIntent(f.player,main.clone()),both=f.api.captureTwoHandIntent(f.player);f.after();main.destroy.push('minecraft:stone');off.props.changed=true;assert.equal(f.api.interactionIntentStillCurrent(f.player,i),true);assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),true);const current=f.container.getItem(0);current.destroy.push('minecraft:dirt');f.container.setItem(0,current);assert.equal(f.api.interactionIntentStillCurrent(f.player,i),false);assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),false);
});
test('unreadable deferred capabilities preserve immediate hand and reject verification',()=>{
 const f=fixture(),s=new f.Stack('x:item',{unreadable:true});f.set(s);f.before();const i=f.api.captureInteractionIntent(f.player,s.clone()),both=f.api.captureTwoHandIntent(f.player);assert.equal(i.hand,'main');assert.ok(both);f.after();assert.equal(f.api.interactionIntentStillCurrent(f.player,i),false);assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),false);
});
test('direct before-safe recipe signature has zero restricted reads; full signature is explicit',()=>{const f=fixture(),s=new f.Stack('x:item');assert.equal(typeof core.stackIntentSignature(s),'string');assert.equal(f.phase.destroy+f.phase.place,0);assert.throws(()=>core.fullStackIntentSignature(s),ReferenceError);});
test('slot pins main and two-hand; off permits slot switch with unchanged contents',()=>{
 const f=fixture(),main=new f.Stack('x:main'),off=new f.Stack('x:off');f.set(main,off);f.container.setItem(1,main);f.before();const m=f.api.captureInteractionIntent(f.player,main.clone()),o=f.api.captureInteractionIntent(f.player,off.clone()),both=f.api.captureTwoHandIntent(f.player);f.after();f.player.selectedSlotIndex=1;assert.equal(f.api.interactionIntentStillCurrent(f.player,m),false);assert.equal(f.api.interactionIntentStillCurrent(f.player,o),true);assert.equal(f.api.twoHandIntentStillCurrent(f.player,both),false);
});
test('two-hand empty, dimension, stance and invalid player handling remains explicit',()=>{
 const f=fixture();f.before();const i=f.api.captureTwoHandIntent(f.player);assert.ok(i);assert.equal(i.main,null);assert.equal(i.off,null);f.after();assert.equal(f.api.twoHandIntentStillCurrent(f.player,i),true);f.player.isSneaking=true;assert.equal(f.api.twoHandIntentStillCurrent(f.player,i),false);f.player.isSneaking=false;f.player.dimension.id='minecraft:nether';assert.equal(f.api.twoHandIntentStillCurrent(f.player,i),false);f.player.isValid=false;assert.equal(f.api.captureTwoHandIntent(f.player),null);
});
test('completely identical hands and nonmatching event metadata reject uncertainty',()=>{
 const f=fixture(),s=new f.Stack('x:item');f.set(s,s);f.before();const i=f.api.captureInteractionIntent(f.player,s.clone());f.after();assert.equal(i.hand,'main');assert.equal(f.api.interactionIntentStillCurrent(f.player,i),false);f.set(s,new f.Stack('x:other'));f.before();const j=f.api.captureInteractionIntent(f.player,new f.Stack('x:item',{nameTag:'unmatched'}));f.after();assert.equal(j.hand,'main');assert.equal(f.api.interactionIntentStillCurrent(f.player,j),false);
});
