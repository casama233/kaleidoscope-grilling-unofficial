import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Stack{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount}}
class Perm{
 constructor(states={}){this.states={...states}}
 getState(id){return this.states[id]}
 withState(id,value){return new Perm({...this.states,[id]:value})}
}
const startup=[],drops=[],randoms=[];
const math=Object.create(Math);math.random=()=>randoms.length?randoms.shift():0;
const system={beforeEvents:{startup:{subscribe(fn){startup.push(fn)}}}};
const EquipmentSlot={Mainhand:'main',Offhand:'off'};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2714_houttuynia_crop_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2714_houttuynia_crop_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['system','ItemStack','EquipmentSlot'],function(){
 this.setExport('system',system);this.setExport('ItemStack',Stack);this.setExport('EquipmentSlot',EquipmentSlot);
},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);await rt.evaluate();
assert.equal(startup.length,1);
let component;
startup[0]({blockComponentRegistry:{registerCustomComponent(id,obj){assert.equal(id,'kaleidoscope_grilling:houttuynia_crop_logic');component=obj}}});
assert.ok(component);

function makeWorld({ground='minecraft:farmland',moisture=7,light=15,age=0,red=false}={}){
 const loc={x:10,y:64,z:10},blocks=new Map();
 const key=(x,y,z)=>x+','+y+','+z;
 const dimension={
  getLightLevel(){return light},
  getBlock(p){return blocks.get(key(p.x,p.y,p.z))},
  setBlockType(p,id){const b=blocks.get(key(p.x,p.y,p.z));if(b)b.typeId=id},
  spawnItem(stack,where){drops.push({stack,where})}
 };
 for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){
  blocks.set(key(10+dx,63,10+dz),{typeId:ground,permutation:new Perm({moisturized_amount:moisture})});
 }
 const block={
  typeId:'kaleidoscope_grilling:houttuynia_crop',dimension,location:loc,
  permutation:new Perm({'kaleidoscope_grilling:age':age,'kaleidoscope_grilling:red_variant':red}),
  setPermutation(p){this.permutation=p}
 };
 blocks.set(key(10,64,10),block);
 return {dimension,block,loc,blocks,key};
}

drops.length=0;randoms.push(.9);
{
 const w=makeWorld({ground:'minecraft:soul_sand',light:0});
 const event={block:w.block,dimension:w.dimension,cancel:false,permutationToPlace:new Perm()};
 component.beforeOnPlayerPlace(event);
 assert.equal(event.cancel,false);
 assert.equal(event.permutationToPlace.getState('kaleidoscope_grilling:age'),0);
 assert.equal(event.permutationToPlace.getState('kaleidoscope_grilling:red_variant'),true);
}

randoms.push(.2);
{
 const w=makeWorld({ground:'minecraft:farmland',light:15});
 const event={block:w.block,dimension:w.dimension,cancel:false,permutationToPlace:new Perm()};
 component.beforeOnPlayerPlace(event);
 assert.equal(event.permutationToPlace.getState('kaleidoscope_grilling:red_variant'),true);
}

{
 const w=makeWorld({ground:'minecraft:farmland',light:7});
 const event={block:w.block,dimension:w.dimension,cancel:false,permutationToPlace:new Perm()};
 component.beforeOnPlayerPlace(event);assert.equal(event.cancel,true);
}

randoms.push(0);
{
 const w=makeWorld({ground:'minecraft:farmland',moisture:7,light:15,age:3,red:false});
 component.onRandomTick({block:w.block,dimension:w.dimension});
 assert.equal(w.block.permutation.getState('kaleidoscope_grilling:age'),4);
}

drops.length=0;
{
 const w=makeWorld({ground:'minecraft:farmland',light:7,age:3});
 component.onRandomTick({block:w.block,dimension:w.dimension});
 assert.equal(w.block.typeId,'minecraft:air');
 assert.equal(drops.length,1);assert.equal(drops[0].stack.typeId,'kaleidoscope_grilling:houttuynia');
}

randoms.push(.999);
{
 const w=makeWorld({ground:'minecraft:farmland',light:15,age:2,red:true});
 let hand=new Stack('minecraft:bone_meal',2);
 const slot={hasItem(){return !!hand},getItem(){return hand},setItem(v){hand=v}};
 const player={getGameMode(){return 'Survival'},getComponent(id){if(id==='minecraft:equippable')return{getEquipmentSlot(h){return h==='main'?slot:{hasItem(){return false}}}}}};
 component.onPlayerInteract({block:w.block,dimension:w.dimension,player});
 assert.equal(w.block.permutation.getState('kaleidoscope_grilling:age'),7);
 assert.equal(w.block.permutation.getState('kaleidoscope_grilling:red_variant'),true);
 assert.equal(hand.amount,1);
}

console.log(JSON.stringify({passed:6,failed:0,scope:'A2.7.14 houttuynia crop runtime'}));
