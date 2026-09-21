import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Stack{
 constructor(typeId,amount=1,fortune=0){this.typeId=typeId;this.amount=amount;this.fortune=fortune}
 getComponent(id){if(id==='minecraft:enchantable')return{getEnchantment:(name)=>String(name).includes('fortune')&&this.fortune>0?{level:this.fortune}:undefined};return undefined}
}
class Perm{
 constructor(states={},typeId='minecraft:air'){this.states={...states};this.type={id:typeId}}
 getState(id){return this.states[id]}
 withState(id,value){return new Perm({...this.states,[id]:value},this.type.id)}
}
const startup=[],breaks=[],drops=[],randoms=[];
const math=Object.create(Math);math.random=()=>randoms.length?randoms.shift():0;
const system={beforeEvents:{startup:{subscribe(fn){startup.push(fn)}}}};
const world={afterEvents:{playerBreakBlock:{subscribe(fn){breaks.push(fn)}}}};
const EquipmentSlot={Mainhand:'main',Offhand:'off',Head:'head'};
const GameMode={Creative:'Creative',Survival:'Survival'};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const shared14=new vm.SourceTextModule(fs.readFileSync(new URL('a2714_houttuynia_crop_core.js',root),'utf8'),{context,identifier:'shared14'});
const shared15=new vm.SourceTextModule(fs.readFileSync(new URL('a2715_canola_crop_core.js',root),'utf8'),{context,identifier:'shared15'});
const shared17=new vm.SourceTextModule(fs.readFileSync(new URL('a2717_onion_crop_core.js',root),'utf8'),{context,identifier:'shared17'});
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2719_sweet_potato_crop_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2719_sweet_potato_crop_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode'],function(){
 this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',Stack);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode);
},{context,identifier:'server'});
await shared15.link(async spec=>spec==='./a2714_houttuynia_crop_core.js'?shared14:null);
await shared17.link(async spec=>spec==='./a2715_canola_crop_core.js'?shared15:null);
await core.link(async spec=>spec==='./a2715_canola_crop_core.js'?shared15:spec==='./a2717_onion_crop_core.js'?shared17:null);
await rt.link(async spec=>spec==='@minecraft/server'?server:core);await rt.evaluate();
assert.equal(startup.length,1);assert.equal(breaks.length,1);
let component;
startup[0]({blockComponentRegistry:{registerCustomComponent(id,obj){assert.equal(id,'kaleidoscope_grilling:sweet_potato_crop_logic');component=obj}}});
assert.ok(component);

function makeWorld({ground='minecraft:farmland',moisture=7,light=15,age=0}={}){
 const loc={x:7,y:64,z:10},blocks=new Map(),key=(x,y,z)=>x+','+y+','+z;
 const dimension={
  getLightLevel(){return light},
  getBlock(p){return blocks.get(key(p.x,p.y,p.z))},
  setBlockType(p,id){const b=blocks.get(key(p.x,p.y,p.z));if(b)b.typeId=id},
  spawnItem(stack,where){drops.push({stack,where})}
 };
 for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++)blocks.set(key(7+dx,63,10+dz),{typeId:ground,permutation:new Perm({moisturized_amount:moisture},ground)});
 const block={typeId:'kaleidoscope_grilling:sweet_potato_crop',dimension,location:loc,permutation:new Perm({'kaleidoscope_grilling:age':age},'kaleidoscope_grilling:sweet_potato_crop'),setPermutation(p){this.permutation=p}};
 blocks.set(key(7,64,10),block);return{dimension,block};
}
function player({hat='kaleidoscope_cookery:straw_hat',mode=GameMode.Survival,boneMeal}={}){
 const head=new Stack(hat),main=boneMeal??undefined;
 const slots={
  head:{hasItem(){return !!head},getItem(){return head}},
  main:{hasItem(){return !!main},getItem(){return main},setItem(v){if(main){main.amount=v?.amount??0}}},
  off:{hasItem(){return false}}
 };
 return {getGameMode(){return mode},getComponent(id){if(id==='minecraft:equippable')return{getEquipment(h){return slots[h]?.getItem?.()},getEquipmentSlot(h){return slots[h]}}}};
}

{
 const w=makeWorld();const e={block:w.block,dimension:w.dimension,cancel:false,permutationToPlace:new Perm({},'kaleidoscope_grilling:sweet_potato_crop')};
 component.beforeOnPlayerPlace(e);assert.equal(e.cancel,false);assert.equal(e.permutationToPlace.getState('kaleidoscope_grilling:age'),0);
}
{
 const w=makeWorld({ground:'minecraft:dirt'});const e={block:w.block,dimension:w.dimension,cancel:false,permutationToPlace:new Perm()};
 component.beforeOnPlayerPlace(e);assert.equal(e.cancel,true);
}
randoms.push(0);
{
 const w=makeWorld({age:5});component.onRandomTick({block:w.block,dimension:w.dimension});
 assert.equal(w.block.permutation.getState('kaleidoscope_grilling:age'),6);
}
randoms.push(.999);
{
 const w=makeWorld({age:2});const p=player({boneMeal:new Stack('minecraft:bone_meal',2)});
 component.onPlayerInteract({block:w.block,dimension:w.dimension,player:p});
 assert.equal(w.block.permutation.getState('kaleidoscope_grilling:age'),7);
}

drops.length=0;randoms.push(.999,0,.5,.9,0,0);
{
 const b={location:{x:1,y:2,z:3},dimension:{spawnItem(stack,where){drops.push({stack,where})}}};
 breaks[0]({block:b,player:player({}),brokenBlockPermutation:new Perm({},'minecraft:short_grass'),itemStackBeforeBreak:new Stack('minecraft:diamond_pickaxe',1,3)});
 assert.equal(randoms.length,0);
 assert.deepEqual(drops.map(x=>[x.stack.typeId,x.stack.amount]),[
  ['kaleidoscope_grilling:canola_seeds',4],['kaleidoscope_grilling:onion',1]
 ]);
}

drops.length=0;randoms.push(.1,.1,.1,.1,.1,.1);
{
 const b={location:{x:1,y:2,z:3},dimension:{spawnItem(stack,where){drops.push({stack,where})}}};
 breaks[0]({block:b,player:player({mode:GameMode.Creative}),brokenBlockPermutation:new Perm({},'minecraft:short_grass'),itemStackBeforeBreak:new Stack('minecraft:stick')});
 assert.equal(drops.length,0);assert.equal(randoms.length,6);
}

console.log(JSON.stringify({passed:6,failed:0,scope:'A2.7.19 sweet potato crop + unified Java-order crop drops'}));
