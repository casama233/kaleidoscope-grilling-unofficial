import {eatingItemId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
/** Production full-skewer selection/display tests; client rendering stays separate. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {PLATE_FOOD_VISUAL_TYPE,PLATE_VISUAL_LAYOUTS,plateVisualPlan,plateVisualPose} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/plate_visual_core.js';
import {RAW_TO_COOKED} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/data.js';
import {GRILL_MODEL_INDEX} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/grill_visual_data.js';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/station_contents_visual_runtime.js',import.meta.url),'utf8');
function fixture(limit=32){
 const row={parts:new Map()},spawned=[],removed=[],writes=[],block={x:2,y:64,z:-3,permutation:{getState:()=> 'north'}};
 block.dimension={id:'minecraft:overworld',spawnEntity(typeId,at,spawnOptions){const e={typeId,isValid:true,spawnOptions,props:{},teleport(location,options){this.location=location;this.options=options},setProperty(k,v){writes.push([k,v]);this.props[k]=v},remove(){this.isValid=false;removed.push(this)}};spawned.push(e);return e}};
 const ctx=vm.createContext({PLATE_FOOD_VISUAL_TYPE,secretVisualState:(stack,reader)=>reader(stack),reader:s=>s.secret,
 metadataSignature:JSON.stringify,captureSkewerMetadata:s=>structuredClone(s),helpers:0,grillingConfig:()=>({contentsHelpers:limit}),system:{currentTick:0},lastCapacityWarning:-1200,console,
 discard(r,k){const old=r.parts.get(k);if(old){old.entity.remove();r.parts.delete(k);ctx.helpers--;}}});
 vm.runInContext(source.slice(source.indexOf('function renderPlate('),source.indexOf('export function syncStationContentsVisual(')),ctx);
 return {row,block,spawned,removed,writes,draw(stack,key='plate/0',count=1){ctx.renderPlate(row,block,key,stack,plateVisualPose(block,Number(key.split('/')[1]),count),plateVisualPlan(stack))}};
}
test('all19 raw/cooked canonical pairs and native eating aliases select exact existing world meshes',()=>{
 for(const [raw,cooked]of Object.entries(RAW_TO_COOKED))for(const [alternate,animations]of [[false,true],[true,true],[false,false]]){
  assert.deepEqual(plateVisualPlan({typeId:eatingItemId(raw,alternate,animations)}),{model:GRILL_MODEL_INDEX[raw]*6,secret:false});
  assert.deepEqual(plateVisualPlan({typeId:eatingItemId(cooked,alternate,animations)}),{model:GRILL_MODEL_INDEX[raw]*6+4,secret:false});
 }
 for(const suffix of ['', '_native_plain','_java_three_alt'])assert.deepEqual(plateVisualPlan({typeId:'kaleidoscope_grilling:secret_skewer'+suffix}),{model:114,secret:true});
 for(const id of [undefined,'minecraft:carrot','external:unknown','toString'])assert.equal(plateVisualPlan({typeId:id}),undefined);
});
test('original1..5 count layouts are bounded; all4 facings rotate positions with their distinct y/yaw',()=>{
 assert.deepEqual(PLATE_VISUAL_LAYOUTS.map(r=>r.length),[0,1,2,3,4,5]);
 const f=fixture();for(let count=1;count<=5;count++)for(let slot=0;slot<count;slot++){
  const cell=PLATE_VISUAL_LAYOUTS[count][slot],positions=[];
  for(const [direction,angle]of Object.entries({south:0,west:90,north:180,east:270})){
   f.block.permutation.getState=()=>direction;const pose=plateVisualPose(f.block,slot,count);positions.push(pose.location);
   assert.equal(pose.location.y,64+cell[1]/16);assert.equal(pose.angle,angle-cell[3]);if(direction==='south'){assert.equal(pose.location.x,2+cell[0]/16);assert.equal(pose.location.z,-3+cell[2]/16)}
  }
  assert.ok(Math.abs(positions[0].x+positions[2].x-5)<1e-9);assert.ok(Math.abs(positions[1].z+positions[3].z+5)<1e-9);
 }
 assert.equal(plateVisualPose(f.block,0,0),undefined);assert.equal(plateVisualPose(f.block,5,5),undefined);
});
test('composed plain secret creates one full-skewer helper with all3 packed foods, never native item equipment',()=>{
 const f=fixture(),stack={typeId:'kaleidoscope_grilling:secret_skewer_native_plain',amount:1,secret:[2053,2794,122],props:{saved:'all metadata stays'}},before=structuredClone(stack);
 f.draw(stack);assert.equal(f.spawned.length,1);const e=f.spawned[0];assert.equal(e.typeId,PLATE_FOOD_VISUAL_TYPE);
 assert.deepEqual(e.props,{'kaleidoscope_grilling:ready':true,'kaleidoscope_grilling:model':114,'kaleidoscope_grilling:secret_0':2053,'kaleidoscope_grilling:secret_1':2794,'kaleidoscope_grilling:secret_2':122});
 assert.equal(f.writes[0][1],false);assert.deepEqual(stack,before);f.draw(stack);assert.equal(f.spawned.length,1);assert.equal(f.writes.length,6);
 stack.secret[0]++;f.draw(stack);assert.equal(f.spawned.length,1);assert.equal(e.props['kaleidoscope_grilling:secret_0'],2054);
});
test('unchanged-yaw count changes reuse helpers; removal retires only missing derived display',()=>{
 const f=fixture(),stack={typeId:Object.values(RAW_TO_COOKED)[0],secret:[]};for(let i=0;i<5;i++)f.draw(stack,'plate/'+i,5);
 assert.equal(f.spawned.length,5);assert.equal(f.row.parts.size,5);const first=f.spawned[0].location;
 f.draw(stack,'plate/0',3);assert.notDeepEqual(f.spawned[0].location,first);f.draw(undefined,'plate/4',4);assert.equal(f.row.parts.size,4);assert.equal(f.removed.length,1);
});
test('count transitions replace only helpers whose authored yaw changed, including3→4→5 and reversals',()=>{
 const stack={typeId:Object.values(RAW_TO_COOKED)[0],amount:1,secret:[],props:{saved:'unchanged'}},before=structuredClone(stack);
 for(const direction of ['south','west','north','east']){
  const f=fixture(5);f.block.permutation.getState=()=>direction;
  for(const count of [1,2,3,4,5,4,3,2,1]){
   const old=new Map([...f.row.parts].map(([key,value])=>[key,{entity:value.entity,yaw:value.spawnYaw}]));
   for(let slot=0;slot<5;slot++)f.draw(slot<count?stack:undefined,'plate/'+slot,count);
   assert.equal(f.row.parts.size,count);assert.deepEqual(stack,before);
   for(let slot=0;slot<count;slot++){
    const key='plate/'+slot,part=f.row.parts.get(key),pose=plateVisualPose(f.block,slot,count),previous=old.get(key);
    assert.equal(part.spawnYaw,-pose.angle);assert.equal(part.entity.spawnOptions.initialRotation,-pose.angle);
    assert.equal(part.entity.options.rotation.y,-pose.angle);assert.deepEqual(part.entity.location,pose.location);
    if(previous){if(previous.yaw===-pose.angle)assert.equal(part.entity,previous.entity);else{assert.notEqual(part.entity,previous.entity);assert.equal(previous.entity.isValid,false);}}
   }
  }
 }
});
test('budget exhaustion and rendering failure do not consume stored stacks',()=>{
 const stack={typeId:Object.keys(RAW_TO_COOKED)[0],amount:1},before=structuredClone(stack),f=fixture(0);f.draw(stack);assert.equal(f.spawned.length,0);assert.deepEqual(stack,before);
 const g=fixture();g.draw(stack);g.spawned[0].setProperty=()=>{throw Error('native rejected')};stack.nameTag='updated';assert.throws(()=>g.draw(stack),/native rejected/);assert.equal(g.row.parts.size,0);
 g.draw(stack);assert.equal(g.spawned.length,2);
});
test('plate bindings remain transient with existing audience/budget/queue and startup cleanup',()=>{
 const p=new URL('../../projects/grilling/gameplay_core/',import.meta.url),bp=JSON.parse(fs.readFileSync(new URL('behavior_pack/entities/plate_food_visual.json',p))),rp=JSON.parse(fs.readFileSync(new URL('resource_pack/entity/plate_food_visual.entity.json',p)));
 assert.ok(Object.hasOwn(bp['minecraft:entity'].components,'minecraft:transient'));assert.deepEqual(bp['minecraft:entity'].components['minecraft:body_rotation_always_follows_head'],{});assert.equal(bp['minecraft:entity'].components['minecraft:body_rotation_blocked'],undefined);assert.equal(bp['minecraft:entity'].components['minecraft:body_rotation_axis_aligned'],undefined);assert.equal(bp['minecraft:entity'].components['minecraft:inventory'],undefined);assert.equal(bp['minecraft:entity'].description.runtime_identifier,undefined);
 assert.equal(rp['minecraft:client_entity'].description.enable_attachables,undefined);assert.equal(rp['minecraft:client_entity'].description.scripts.initialize,undefined);
 assert.ok(source.includes('for(const type of [TYPE,RACK_TOOL_VISUAL_TYPE,PLATE_FOOD_VISUAL_TYPE])'));assert.ok(source.includes('configurePlateVisualDirty(markStationContentsDirty)'));
 assert.ok(source.includes('plateVisualPose(block,i,rows.length)'));assert.equal((source.match(/system\.runInterval\(pump,1\)/g)??[]).length,1);
});

test('plate-only animation owns one static horizontal root and exact reviewed post-scale offset',()=>{
 const p=new URL('../../projects/grilling/gameplay_core/resource_pack/animations/plate_food_visual.animation.json',import.meta.url),clips=JSON.parse(fs.readFileSync(p)).animations;
 assert.deepEqual(Object.keys(clips),['animation.kg_station.plate_food']);
 assert.deepEqual(clips['animation.kg_station.plate_food'],{loop:true,bones:{root:{scale:1.2,position:[0,"q.property('kaleidoscope_grilling:model') == 114 ? -1.8 : -0.6",1.8]}}});
});

test('new plate helpers seed exact facing plus authored slot yaw at spawn, without altering other stations',()=>{
 const stack={typeId:Object.keys(RAW_TO_COOKED)[0],secret:[]};
 for(const direction of ['south','west','north','east'])for(let count=1;count<=5;count++){
  const f=fixture();f.block.permutation.getState=()=>direction;
  for(let slot=0;slot<count;slot++){f.draw(stack,'plate/'+slot,count);const pose=plateVisualPose(f.block,slot,count),e=f.spawned[slot];assert.deepEqual(Object.keys(e.spawnOptions),['initialRotation']);assert.equal(e.spawnOptions.initialRotation,-pose.angle);assert.equal(e.options.rotation.y,-pose.angle);}
 }
 assert.equal((source.match(/initialRotation:-at.angle/g)??[]).length,1);
});
