import {canonicalFoodId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {GRILL_MODEL_INDEX} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/grill_visual_data.js';
import {grillVisualStage,grillSlotPlan,grillSlotLocation,nearGrill,createGrillDisplayController} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/grill_visual_core.js';
const block={location:{x:0,y:80,z:0},dimension:{id:'minecraft:overworld'}};
const stack=id=>({typeId:id,amount:1});
const plans=()=>[0,1,2].map(i=>grillSlotPlan(stack(Object.keys(GRILL_MODEL_INDEX)[i]),{phase:0,flips:0},i));
function fixture(options={}){
 const entities=[],writes=[];let failApply=false,failRemove=false;
 const controller=createGrillDisplayController({spawn(b,location){const e={id:entities.length,isValid:true,location};entities.push(e);return e;},
 apply(e,b,pose,plan){if(failApply)throw Error('write unavailable');writes.push({id:e.id,pose,plan});},
 remove(e){if(failRemove)throw Error('remove unavailable');e.isValid=false;},...options});
 return {controller,entities,writes,set failApply(v){failApply=v;},set failRemove(v){failRemove=v;}};
}
test('19 fixed raw skewers use six Java cooking stages, never eating bite stages',()=>{
 assert.equal(Object.keys(GRILL_MODEL_INDEX).length,19);
 const phases=[{phase:0},{phase:1,flips:0},{phase:1,flips:1},{phase:1,flips:2},{phase:2,flips:4},{phase:3,flips:4}];
 for(const [id,index]of Object.entries(GRILL_MODEL_INDEX))for(let stage=0;stage<6;stage++)assert.equal(grillSlotPlan(stack(id),phases[stage],0).model,index*6+stage);
 assert.equal(grillVisualStage({phase:1,flips:4}),4);
 assert.equal(grillSlotPlan(stack('minecraft:diamond'),{phase:0},0),undefined);
 assert.equal(grillSlotPlan(stack('kaleidoscope_grilling:secret_skewer'),{phase:2},1).model,114);
});
test('holes keep their native slot; clearing removes only that display',()=>{
 const f=fixture(),p=plans();f.controller.update('one',block,[p[0],undefined,p[2]],0);
 assert.deepEqual(f.writes.map(w=>w.plan.slot),[0,2]);assert.equal(f.controller.size,2);
 f.controller.update('one',block,[undefined,undefined,p[2]],5);assert.equal(f.controller.size,1);assert.equal(f.entities[1].isValid,true);
});
test('unchanged data does not rewrite properties; phase/flip changes reuse helpers',()=>{
 const f=fixture(),p=plans();f.controller.update('one',block,p,0);f.controller.update('one',block,p,5);assert.equal(f.writes.length,3);
 f.controller.update('one',block,p.map(r=>({...r,model:r.model+4,flips:4})),10);assert.equal(f.writes.length,6);assert.equal(f.entities.length,3);
});
test('all four directions preserve Java 3/8/13 pixel slot ordering',()=>{
 const expected={north:[.1875,.5],east:[.5,.1875],south:[.8125,.5],west:[.5,.8125]};
 for(const [d,[x,z]]of Object.entries(expected)){
  const p=grillSlotLocation(block,0,d).location;assert.ok(Math.abs(p.x-x)<1e-9,d);assert.ok(Math.abs(p.z-z)<1e-9,d);assert.equal(p.y,80.3125);
  const middle=grillSlotLocation(block,1,d).location;assert.equal(middle.x,.5);assert.equal(middle.z,.5);
 }
});
test('observers are restricted by dimension and radius; no audience is quiet',()=>{
 assert.equal(nearGrill(block,[]),false);assert.equal(nearGrill(block,[{dimensionId:'minecraft:nether',x:0,y:80,z:0}]),false);
 assert.equal(nearGrill(block,[{dimensionId:block.dimension.id,x:48.5,y:80,z:.5}]),true);
 assert.equal(nearGrill(block,[{dimensionId:block.dimension.id,x:48.6,y:80,z:.5}]),false);
});
test('unloaded/destroyed stations expire; touching one never preserves another',()=>{
 const f=fixture();f.controller.update('one',block,plans(),0);f.controller.update('two',block,plans(),0);f.controller.touch('one',8);f.controller.sweep(9);
 assert.equal(f.controller.size,3);f.controller.clear('one');f.controller.clear('one');assert.equal(f.controller.size,0);
});
test('invalid transient helpers rebuild without resetting or changing native items',()=>{
 const f=fixture(),p=plans();f.controller.update('one',block,p,0);f.entities[0].isValid=false;f.controller.update('one',block,p,5);
 assert.equal(f.controller.size,3);assert.equal(f.entities.length,4);assert.deepEqual(p,plans());
});
test('failed display writes dispose transient state and retry next tick',()=>{
 const f=fixture();f.failApply=true;f.controller.update('one',block,plans(),0);assert.equal(f.controller.size,0);
 f.failApply=false;f.controller.update('one',block,plans(),5);assert.equal(f.controller.size,3);
});
test('removal failures retain cap accounting until a confirmed retry',()=>{
 const f=fixture({maxHelpers:3});f.controller.update('one',block,plans(),0);f.failRemove=true;f.controller.clear('one');assert.equal(f.controller.size,3);
 f.controller.update('two',block,plans(),5);assert.equal(f.entities.length,3);f.failRemove=false;f.controller.clear('one');f.controller.update('two',block,plans(),10);assert.equal(f.controller.size,3);
});
test('display reads never allocate inventory, rebind its ledger or ignore quarantine',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/family_station_storage.js',import.meta.url),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function))/g,'');
 const data=new Map(),entities=new Map();let writes=0,spawns=0;
 const context=vm.createContext({canonicalFoodId,world:{getDynamicProperty:k=>data.get(k),setDynamicProperty(){writes++;throw Error('display must not write');},getEntity:k=>entities.get(k)},system:{currentTick:0},console});vm.runInContext(source,context);
 const key='kaleidoscope_grilling:storage_v1/minecraft:overworld/0/80/0';
 const b={...block,typeId:'kaleidoscope_grilling:grill',getComponent(){},dimension:{...block.dimension,spawnEntity(){spawns++;},getEntities(){return [...entities.values()];}}};
 context.block=b;assert.equal(vm.runInContext('peekStationContainer(block)',context),undefined);
 const mark={v:1,key,block:b.typeId,token:'original'};const native={size:3,getItem(){return stack(Object.keys(GRILL_MODEL_INDEX)[0]);}};
 const entity={id:'persisted',typeId:'kaleidoscope_grilling:inventory_grill_v1',location:{x:.5,y:80.25,z:.5},dimension:b.dimension,getDynamicProperty(){return JSON.stringify(mark);},getComponent(){return {container:native};}};
 entities.set('persisted',entity);data.set(key,JSON.stringify({...mark,entity:'old-id'}));assert.equal(vm.runInContext('peekStationContainer(block)',context),native);
 assert.equal(JSON.parse(data.get(key)).entity,'old-id');assert.equal(writes,0);assert.equal(spawns,0);
 data.set(key,JSON.stringify({...mark,entity:'persisted',quarantine:'ambiguous debit'}));assert.throws(()=>vm.runInContext('peekStationContainer(block)',context),/quarantined/);
});
