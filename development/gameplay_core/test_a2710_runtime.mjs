import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Stack{
 constructor(typeId,amount=1,looting=0){this.typeId=typeId;this.amount=amount;this.looting=looting}
 getComponent(id){
  if(id==='minecraft:enchantable')return{getEnchantment:(name)=>String(name).includes('looting')&&this.looting>0?{level:this.looting}:undefined};
  return undefined;
 }
}
const dyn=new Map(),beforeListeners=[],dieListeners=[],runs=[],drops=[],randoms=[];
const math=Object.create(Math);math.random=()=>randoms.length?randoms.shift():0;
const world={
 beforeEvents:{playerInteractWithBlock:{subscribe(fn){beforeListeners.push(fn)}}},
 afterEvents:{entityDie:{subscribe(fn){dieListeners.push(fn)}}},
 getDynamicProperty(k){return dyn.get(k)}
};
const system={currentTick:100,run(fn){runs.push(fn)}};
const EquipmentSlot={Mainhand:'main'};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2710_chicken_acquisition_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2710_chicken_acquisition_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot'],function(){
 this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',Stack);this.setExport('EquipmentSlot',EquipmentSlot);
},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);await rt.evaluate();

assert.equal(beforeListeners.length,1);assert.equal(dieListeners.length,1);

function playerWith(stack){
 let hand=stack;
 const slot={hasItem(){return !!hand},getItem(){return hand}};
 return {typeId:'minecraft:player',getComponent(id){if(id==='minecraft:equippable')return{getEquipmentSlot(){return slot}}}};
}
function board(){
 const loc={x:2,y:65,z:-4};
 const dimension={
  id:'minecraft:overworld',
  getBlock(){return block},
  spawnItem(stack,location){drops.push({stack,location})}
 };
 const block={typeId:'kaleidoscope_cookery:chopping_board',dimension,location:loc,x:2,y:65,z:-4};
 return block;
}
const key='kc_station:minecraft:overworld:2,65,-4';
const done={input:'minecraft:chicken',cuts:4,max:4,result:{id:'kaleidoscope_cookery:raw_cut_small_meats',count:2},extension:false};
function flush(){while(runs.length)runs.shift()()}
function reset(){dyn.clear();runs.length=0;drops.length=0;randoms.length=0;system.currentTick++}

reset();
{
 const b=board(),p=playerWith(new Stack('kaleidoscope_cookery:iron_kitchen_knife'));
 dyn.set(key,JSON.stringify(done));beforeListeners[0]({block:b,player:p,itemStack:p.getComponent('minecraft:equippable').getEquipmentSlot().getItem(),isFirstEvent:true});
 assert.equal(runs.length,1);dyn.delete(key);randoms.push(0);flush();
 assert.equal(drops.length,1);assert.equal(drops[0].stack.typeId,'kaleidoscope_grilling:chicken_skin');assert.equal(drops[0].stack.amount,1);
}

reset();
{
 const b=board(),p=playerWith(new Stack('kaleidoscope_cookery:diamond_kitchen_knife'));
 dyn.set(key,JSON.stringify(done));
 const e={block:b,player:p,itemStack:new Stack('kaleidoscope_cookery:diamond_kitchen_knife'),isFirstEvent:true};
 beforeListeners[0](e);beforeListeners[0](e);assert.equal(runs.length,1);
 dyn.delete(key);randoms.push(.999);flush();assert.equal(drops[0].stack.amount,3);
}

reset();
{
 const b=board(),p=playerWith(new Stack('kaleidoscope_cookery:gold_kitchen_knife'));
 dyn.set(key,JSON.stringify({...done,cuts:3}));beforeListeners[0]({block:b,player:p,isFirstEvent:true});assert.equal(runs.length,0);
 dyn.set(key,JSON.stringify(done));beforeListeners[0]({block:b,player:p,isFirstEvent:false});assert.equal(runs.length,0);
}

reset();
{
 const b=board(),p=playerWith(new Stack('kaleidoscope_cookery:netherite_kitchen_knife'));
 dyn.set(key,JSON.stringify(done));beforeListeners[0]({block:b,player:p,isFirstEvent:true});flush();assert.equal(drops.length,0);
}

reset();
{
 const dimension={spawnItem(stack,location){drops.push({stack,location})}};
 const dead={typeId:'minecraft:chicken',location:{x:1,y:2,z:3},dimension};
 const killer=playerWith(new Stack('kaleidoscope_cookery:diamond_kitchen_knife',1,2));
 randoms.push(.999,.999);dieListeners[0]({deadEntity:dead,damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,1);assert.equal(drops[0].stack.typeId,'kaleidoscope_grilling:chicken_wing');assert.equal(drops[0].stack.amount,4);
}

reset();
{
 const dimension={spawnItem(stack,location){drops.push({stack,location})}};
 const dead={typeId:'minecraft:chicken',location:{x:0,y:0,z:0},dimension};
 const killer=playerWith(new Stack('kaleidoscope_cookery:iron_kitchen_knife'));
 randoms.push(0,0);
 dieListeners[0]({deadEntity:dead,damageSource:{damagingEntity:killer,damagingProjectile:{typeId:'minecraft:arrow'}}});
 assert.equal(drops.length,1);assert.equal(drops[0].stack.typeId,'kaleidoscope_grilling:chicken_wing');
 drops.length=0;
 killer.getComponent=()=>({getEquipmentSlot(){return{hasItem(){return true},getItem(){return new Stack('minecraft:diamond_sword')}}}});
 dieListeners[0]({deadEntity:dead,damageSource:{damagingEntity:killer}});assert.equal(drops.length,0);
}

console.log(JSON.stringify({passed:6,failed:0,scope:'A2.7.10 chicken acquisition runtime'}));
