import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const EquipmentSlot={Offhand:'offhand'};
const GameMode={Creative:'creative',Survival:'survival'};
const context=vm.createContext({console,Map,Object,Array,Number,String,Boolean,Error});
const mod=new vm.SourceTextModule(
 fs.readFileSync(new URL('./a2735_player_io.js',import.meta.url),'utf8'),
 {context,identifier:'player-io'}
);
const server=new vm.SyntheticModule(['EquipmentSlot','GameMode'],function(){
 this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode);
},{context,identifier:'server'});
await mod.link(spec=>spec==='@minecraft/server'?server:Promise.reject(new Error(spec)));
await mod.evaluate();
const io=mod.namespace;

function player(){
 const inv=[{typeId:'minecraft:stick',amount:2},undefined,{typeId:'minecraft:apple',amount:1}];
 let off={typeId:'minecraft:torch',amount:3};
 return {
  selectedSlotIndex:2,
  mode:'survival',
  getComponent(id){
   if(id==='minecraft:inventory')return {container:{
    getItem(i){return inv[i]},
    setItem(i,v){inv[i]=v}
   }};
   if(id==='minecraft:equippable')return {
    getEquipment(slot){assert.equal(slot,'offhand');return off},
    setEquipment(slot,v){assert.equal(slot,'offhand');off=v}
   };
  },
  getGameMode(){return this.mode},
  inv(){return inv},
  off(){return off}
 };
}

const p=player();
assert.equal(io.playerInventory(p).getItem(2).typeId,'minecraft:apple');
assert.equal(io.getMainHand(p).typeId,'minecraft:apple');
assert.equal(io.getOffHand(p).typeId,'minecraft:torch');

io.setMainHand(p,{typeId:'minecraft:carrot',amount:1});
assert.equal(p.inv()[2].typeId,'minecraft:carrot');
io.setOffHand(p,{typeId:'minecraft:shield',amount:1});
assert.equal(p.off().typeId,'minecraft:shield');

assert.equal(io.getHand(p,'main').typeId,'minecraft:carrot');
assert.equal(io.getHand(p,'off').typeId,'minecraft:shield');
assert.equal(io.findHand(p,'minecraft:carrot'),'main');
assert.equal(io.findHand(p,'minecraft:shield'),'off');
assert.equal(io.findHand(p,'minecraft:diamond'),null);
assert.equal(io.findHandEntry(p,'minecraft:shield').name,'off');

io.setHand(p,'main',{typeId:'minecraft:bread',amount:1});
assert.equal(io.getMainHand(p).typeId,'minecraft:bread');

assert.equal(io.isCreative(p),false);
p.mode='creative';assert.equal(io.isCreative(p),true);

console.log(JSON.stringify({passed:13,failed:0,scope:'A2.7.35 shared selected-main/offhand/creative player IO'}));
