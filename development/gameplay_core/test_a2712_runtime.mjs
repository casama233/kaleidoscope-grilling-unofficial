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
const dieListeners=[],drops=[],randoms=[];
const math=Object.create(Math);math.random=()=>randoms.length?randoms.shift():0;
const world={afterEvents:{entityDie:{subscribe(fn){dieListeners.push(fn)}}}};
const EquipmentSlot={Mainhand:'main'};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const a2710=new vm.SourceTextModule(fs.readFileSync(new URL('a2710_chicken_acquisition_core.js',root),'utf8'),{context,identifier:'a2710'});
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2712_remaining_knife_drops_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2712_remaining_knife_drops_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['world','ItemStack','EquipmentSlot'],function(){
 this.setExport('world',world);this.setExport('ItemStack',Stack);this.setExport('EquipmentSlot',EquipmentSlot);
},{context,identifier:'server'});
await rt.link(async spec=>{
 if(spec==='@minecraft/server')return server;
 if(spec==='./a2710_chicken_acquisition_core.js')return a2710;
 if(spec==='./a2712_remaining_knife_drops_core.js')return core;
 throw new Error('unexpected import '+spec);
});
await rt.evaluate();
assert.equal(dieListeners.length,1);

function playerWith(stack){
 let hand=stack;
 const slot={hasItem(){return !!hand},getItem(){return hand}};
 return {typeId:'minecraft:player',getComponent(id){if(id==='minecraft:equippable')return{getEquipmentSlot(){return slot}}}};
}
function dead(typeId){
 const dimension={spawnItem(stack,location){drops.push({stack,location})}};
 return {typeId,location:{x:1,y:2,z:3},dimension};
}
function reset(){drops.length=0;randoms.length=0}

reset();
{
 const killer=playerWith(new Stack('kaleidoscope_cookery:diamond_kitchen_knife',1,2));
 randoms.push(.999,.999);
 dieListeners[0]({deadEntity:dead('minecraft:cow'),damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,1);
 assert.equal(drops[0].stack.typeId,'kaleidoscope_cookery:raw_cow_offal');
 assert.equal(drops[0].stack.amount,4);
}

reset();
{
 const killer=playerWith(new Stack('kaleidoscope_cookery:iron_kitchen_knife'));
 randoms.push(0,.499);
 dieListeners[0]({deadEntity:dead('minecraft:squid'),damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,1);
 assert.equal(drops[0].stack.typeId,'kaleidoscope_grilling:squid_tentacle');
 assert.equal(drops[0].stack.amount,2);
}

reset();
{
 const killer=playerWith(new Stack('kaleidoscope_cookery:netherite_kitchen_knife',1,3));
 randoms.push(.999,.999,.5);
 dieListeners[0]({deadEntity:dead('minecraft:squid'),damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,0);
}

reset();
{
 const killer=playerWith(new Stack('minecraft:diamond_sword'));
 dieListeners[0]({deadEntity:dead('minecraft:cow'),damageSource:{damagingEntity:killer}});
 dieListeners[0]({deadEntity:dead('minecraft:squid'),damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,0);
}

reset();
{
 const killer=playerWith(new Stack('kaleidoscope_cookery:gold_kitchen_knife'));
 dieListeners[0]({deadEntity:dead('minecraft:pig'),damageSource:{damagingEntity:killer}});
 assert.equal(drops.length,0);
}

console.log(JSON.stringify({passed:5,failed:0,scope:'A2.7.12 cow offal + squid tentacle knife drops'}));
