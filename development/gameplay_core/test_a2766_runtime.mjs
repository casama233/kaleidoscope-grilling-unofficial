import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const BP=path.join(ROOT,'projects/grilling/gameplay_core/behavior_pack');
const scripts=path.join(BP,'scripts');
const U='kaleidoscope_grilling:uses',V='kaleidoscope_grilling:variant',L='kaleidoscope_grilling:seasonings';
const ids=new Set(fs.readdirSync(path.join(BP,'items')).filter(f=>f.endsWith('.json')).map(f=>JSON.parse(fs.readFileSync(path.join(BP,'items',f),'utf8'))['minecraft:item'].description.identifier));
let failConstruct=false,failMetadata=false,failWorld=false,failInventory=false;
class ItemStack{
 constructor(id,amount=1){if(!ids.has(id)||failConstruct)throw new Error('missing_item:'+id);this.typeId=id;this.amount=amount;this.props={};this.rawLore=[];this.keepOnDeath=false;this.lockMode='none';this.destroy=[];this.place=[];}
 clone(){const out=Object.create(ItemStack.prototype);Object.assign(out,structuredClone({...this}));return out;}
 getDynamicPropertyIds(){return Object.keys(this.props)}
 getDynamicProperty(id){return this.props[id]}
 setDynamicProperty(id,value){if(failMetadata)throw new Error('metadata_write');this.props[id]=structuredClone(value)}
 getRawLore(){return structuredClone(this.rawLore)}
 getLore(){return this.rawLore.map(x=>typeof x==='string'?x:JSON.stringify(x))}
 setLore(v){this.rawLore=structuredClone(v)}
 getCanDestroy(){return [...this.destroy]}
 getCanPlaceOn(){return [...this.place]}
 setCanDestroy(v){this.destroy=[...v]}
 setCanPlaceOn(v){this.place=[...v]}
 getComponent(){return undefined}
}
const listeners={},queue=[],props=new Map();
const signal=name=>({subscribe:fn=>{(listeners[name]??=[]).push(fn)}});
const world={beforeEvents:{playerInteractWithBlock:signal('interact'),playerBreakBlock:signal('break'),explosion:signal('explosion')},
 getAbsoluteTime:()=>100,getDynamicProperty:k=>props.get(k),setDynamicProperty(k,v){if(failWorld){failWorld=false;throw new Error('world_write')}if(v===undefined)props.delete(k);else props.set(k,v)}};
const system={currentTick:100,run:fn=>queue.push(fn)};
const context=vm.createContext({console});
const exposed={ItemStack,world,system,EquipmentSlot:{Offhand:'offhand'},GameMode:{Creative:'creative'}};
const server=new vm.SyntheticModule(Object.keys(exposed),function(){for(const[k,v]of Object.entries(exposed))this.setExport(k,v)},{context});
const cache=new Map();
function getModule(p){
 if(!cache.has(p))cache.set(p,new vm.SourceTextModule(fs.readFileSync(p,'utf8'),{identifier:p,context}));
 return cache.get(p);
}
async function load(name){const m=getModule(path.join(scripts,name));if(m.status==='unlinked')await m.link((s,parent)=>s==='@minecraft/server'?server:getModule(path.resolve(path.dirname(parent.identifier),s)));if(m.status==='linked')await m.evaluate();return m.namespace;}
const core=await load('a2766_special_seasoning_visual_core.js');
const runtime=await load('a2766_special_seasoning_visual_runtime.js');
const rack=await load('a2746_advanced_rack_core.js');
await load('a2750_cookery_cuisine_runtime.js');
let n=0,states=0;
function reset(){props.clear();queue.length=0;failConstruct=failMetadata=failWorld=failInventory=false;}
function test(name,fn){reset();fn();n++;console.log('PASS '+name)}
function bottle(uses=1,variant=7){const s=new ItemStack(core.specialSeasoningVisualId(uses,variant));s.setDynamicProperty(U,uses);s.setDynamicProperty(V,variant);s.setDynamicProperty(L,JSON.stringify(['kaleidoscope_grilling:onion_powder']));return s;}
function fixture(uses=1,creative=false){
 const cells=[bottle(uses),undefined];
 const inventory={size:2,getItem:i=>cells[i]?.clone(),setItem(i,s){if(failInventory){failInventory=false;throw new Error('inventory_write')}cells[i]=s?.clone()}};
 const player={selectedSlotIndex:0,getGameMode:()=>creative?'creative':'survival',getComponent:id=>id==='minecraft:inventory'?{container:inventory}:{getEquipment:()=>undefined},onScreenDisplay:{setActionBar(){}},playAnimation(){},playSound(){}};
 const dimension={id:'minecraft:overworld',getBlock:()=>block};
 const block={x:0,y:64,z:0,location:{x:0,y:64,z:0},typeId:'kaleidoscope_cookery:pot',dimension,permutation:{getState:()=>false}};
 function click(beforeRun=()=>{}){const event={player,block,isFirstEvent:true,cancel:false};for(const f of listeners.interact)f(event);assert.equal(event.cancel,true);beforeRun();while(queue.length)queue.shift()();}
 return {cells,player,click};
}
test('all 128 live uses/variant combinations resolve and stay Rack-compatible',()=>{
 const seen=new Set();
 for(let uses=0;uses<16;uses++)for(let variant=0;variant<8;variant++){
  const id=core.specialSeasoningVisualId(uses,variant);assert(ids.has(id),id);assert.equal(rack.rackItemKind(id),'seasoning');
  const a=JSON.parse(fs.readFileSync(path.join(ROOT,'projects/grilling/gameplay_core/resource_pack/attachables',id.split(':')[1]+'.attachable.json'),'utf8'));
  assert.equal(a['minecraft:attachable'].description.identifier,id);seen.add(id);states++;
 }
 assert.equal(seen.size,64);
});
test('all variants retain uses, ingredients and variant after every active decrement',()=>{
 for(let v=0;v<8;v++)for(let u=0;u<15;u++){
  const source=bottle(u,v),before=JSON.stringify(source);const next=runtime.retargetSpecialSeasoningStack(source,u+1,v);
  assert(next);assert.equal(next.getDynamicProperty(U),u+1);assert.equal(next.getDynamicProperty(V),v);assert.equal(next.getDynamicProperty(L),source.getDynamicProperty(L));assert.equal(JSON.stringify(source),before);
 }
});
test('retarget preserves raw localized lore, custom name, vector data and adventure restrictions',()=>{
 const s=bottle();s.nameTag='測試';s.setLore([{translate:'example.translation'},'custom']);s.setDynamicProperty('example:vector',{x:1,y:2,z:3});s.keepOnDeath=true;s.lockMode='inventory';s.setCanDestroy(['minecraft:dirt']);s.setCanPlaceOn(['minecraft:stone']);
 const out=runtime.retargetSpecialSeasoningStack(s,2);assert(out);assert.equal(out.nameTag,s.nameTag);assert.deepEqual(out.getRawLore(),s.getRawLore());assert.deepEqual(out.getDynamicProperty('example:vector'),s.getDynamicProperty('example:vector'));assert.equal(out.keepOnDeath,true);assert.equal(out.lockMode,'inventory');assert.deepEqual(out.getCanDestroy(),s.getCanDestroy());assert.deepEqual(out.getCanPlaceOn(),s.getCanPlaceOn());
});
test('missing ItemStack definition cancels without touching original',()=>{const s=bottle(),before=JSON.stringify(s);failConstruct=true;assert.equal(runtime.retargetSpecialSeasoningStack(s,2),undefined);assert.equal(JSON.stringify(s),before)});
test('metadata write failure returns no partial bottle',()=>{const s=bottle(),before=JSON.stringify(s);failMetadata=true;assert.equal(runtime.retargetSpecialSeasoningStack(s,2),undefined);assert.equal(JSON.stringify(s),before)});
test('invalid stacked visual bottle is rejected rather than losing items',()=>{const s=bottle();s.amount=2;assert.equal(runtime.retargetSpecialSeasoningStack(s,2),undefined)});
test('normal Cookery use updates hand and station exactly once',()=>{const f=fixture();f.click();assert.equal(f.cells[0].getDynamicProperty(U),2);assert.equal(props.size,1);assert(JSON.parse([...props.values()][0]).seasoning.length===1)});
test('last use returns empty bottle',()=>{const f=fixture(15);f.click();assert.equal(f.cells[0].typeId,'kaleidoscope_grilling:empty_seasoning_bottle');assert.equal(props.size,1)});
test('creative use does not consume seasoning',()=>{const f=fixture(1,true),before=JSON.stringify(f.cells[0]);f.click();assert.equal(JSON.stringify(f.cells[0]),before);assert.equal(props.size,1)});
test('preparing the new bottle fails before station is modified',()=>{const f=fixture(),before=JSON.stringify(f.cells[0]);failConstruct=true;f.click();assert.equal(props.size,0);assert.equal(JSON.stringify(f.cells[0]),before)});
test('metadata failure cannot grant free seasoning to Cookery',()=>{const f=fixture(),before=JSON.stringify(f.cells[0]);failMetadata=true;f.click();assert.equal(props.size,0);assert.equal(JSON.stringify(f.cells[0]),before)});
test('world write failure rolls back hand and old station data',()=>{const f=fixture(),before=JSON.stringify(f.cells[0]);failWorld=true;f.click();assert.equal(props.size,0);assert.equal(JSON.stringify(f.cells[0]),before)});
test('inventory write failure leaves station and hand unchanged',()=>{const f=fixture(),before=JSON.stringify(f.cells[0]);failInventory=true;f.click();assert.equal(props.size,0);assert.equal(JSON.stringify(f.cells[0]),before)});
test('switching selected slot during defer cancels use',()=>{const f=fixture(),before=JSON.stringify(f.cells[0]);f.click(()=>{f.player.selectedSlotIndex=1});assert.equal(props.size,0);assert.equal(JSON.stringify(f.cells[0]),before)});
test('changing ingredients during defer cancels use',()=>{const f=fixture();f.click(()=>f.cells[0].setDynamicProperty(L,'[]'));assert.equal(props.size,0);assert.equal(f.cells[0].getDynamicProperty(U),1)});
console.log(JSON.stringify({tests:n,activeStateCombinations:states,mockedMinecraftAPI:true,minecraft_tested:false}));
