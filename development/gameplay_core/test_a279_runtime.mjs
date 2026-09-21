import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.nameTag='';this.props={};this.lore=[]}
 clone(){const x=new Stack(this.typeId,this.amount);x.nameTag=this.nameTag;x.props={...this.props};x.lore=[...this.lore];return x}
 getLore(){return [...this.lore]}
 getDynamicPropertyIds(){return Object.keys(this.props)}
 getDynamicProperty(id){return this.props[id]}
}
class Perm{
 constructor(states={}){this.states={...states}}
 withState(k,v){return new Perm({...this.states,[k]:v})}
 getState(k){return this.states[k]}
}
const dyn=new Map(),runs=[],warnings=[];
const world={
 getDynamicProperty(k){return dyn.get(k)},
 setDynamicProperty(k,v){if(v===undefined)dyn.delete(k);else dyn.set(k,v)}
};
const system={run(fn){runs.push(fn)}};
const GameMode={Creative:'creative',Survival:'survival'},EquipmentSlot={Mainhand:'main'};
const context=vm.createContext({console:{warn:x=>warnings.push(String(x)),log:console.log},JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a279_beef_board_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a279_beef_board_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['world','system','GameMode','EquipmentSlot'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('GameMode',GameMode);this.setExport('EquipmentSlot',EquipmentSlot)},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);await rt.evaluate();
const {tryScheduleBeefBoardOverride}=rt.namespace;

function setup({amount=3,mode='survival',state,failSet=false}={}){
 dyn.clear();runs.length=0;warnings.length=0;
 let hand=new Stack('minecraft:beef',amount);
 const slot={hasItem(){return !!hand},getItem(){return hand?.clone()},setItem(v){if(failSet)throw new Error('set failed');hand=v?.clone()}};
 const dim={id:'minecraft:overworld',getBlock(){return block}};
 const block={typeId:'kaleidoscope_cookery:chopping_board',dimension:dim,x:1,y:64,z:2,location:{x:1,y:64,z:2},permutation:new Perm({}),setPermutation(p){this.permutation=p}};
 const player={selectedSlotIndex:0,getGameMode(){return mode},getComponent(id){if(id==='minecraft:equippable')return{getEquipmentSlot(){return slot}}},playSound(){}};
 const key='kc_station:minecraft:overworld:1,64,2';if(state!==undefined)dyn.set(key,JSON.stringify(state));
 const event={cancel:false,block,player,itemStack:hand.clone(),isFirstEvent:true};
 return {event,block,player,key,getHand:()=>hand,setHand:v=>{hand=v}};
}
function flush(){while(runs.length)runs.shift()()}

{
 const x=setup();assert.equal(tryScheduleBeefBoardOverride(x.event),true);assert.equal(x.event.cancel,true);assert.equal(runs.length,1);flush();
 const st=JSON.parse(dyn.get(x.key));assert.equal(st.result.id,'kaleidoscope_grilling:beef_chunks');assert.equal(st.result.count,2);assert.equal(st.max,4);
 assert.equal(x.getHand().amount,2);assert.equal(x.block.permutation.getState('kaleidoscope_cookery:board_model'),0);assert.equal(x.block.permutation.getState('kaleidoscope_cookery:cut_stage'),0);
}
{
 const x=setup({amount:1,mode:'creative'});assert.equal(tryScheduleBeefBoardOverride(x.event),true);flush();assert.equal(x.getHand().amount,1);
}
{
 const x=setup();x.event.isFirstEvent=false;assert.equal(tryScheduleBeefBoardOverride(x.event),true);assert.equal(x.event.cancel,true);assert.equal(runs.length,0);
}
{
 const built={input:'minecraft:beef',cuts:4,max:4,result:{id:'kaleidoscope_cookery:raw_cow_offal',count:2},extension:false};
 const x=setup({state:built});x.setHand(new Stack('kaleidoscope_cookery:iron_kitchen_knife',1));x.event.itemStack=x.getHand().clone();
 assert.equal(tryScheduleBeefBoardOverride(x.event),true);flush();const st=JSON.parse(dyn.get(x.key));assert.equal(st.result.id,'kaleidoscope_grilling:beef_chunks');assert.equal(st.cuts,4);assert.equal(x.getHand().typeId,'kaleidoscope_cookery:iron_kitchen_knife');
}
{
 const x=setup();assert.equal(tryScheduleBeefBoardOverride(x.event),true);x.setHand(new Stack('minecraft:potato',3));flush();assert.equal(dyn.has(x.key),false);assert.equal(x.getHand().typeId,'minecraft:potato');
}
{
 const x=setup({state:{input:'minecraft:potato',cuts:0,max:4,result:{id:'kaleidoscope_grilling:potato_slice',count:3}}});assert.equal(tryScheduleBeefBoardOverride(x.event),false);assert.equal(x.event.cancel,false);
}
{
 const x=setup({failSet:true});const before=x.block.permutation;assert.equal(tryScheduleBeefBoardOverride(x.event),true);flush();assert.equal(dyn.has(x.key),false);assert.equal(x.block.permutation,before);assert.ok(warnings.length>=1);
}
console.log(JSON.stringify({passed:7,failed:0,scope:'A2.7.9 beef chopping-board override runtime'}));
