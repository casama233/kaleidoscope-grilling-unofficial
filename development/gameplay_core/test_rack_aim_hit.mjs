/** Pure production selection geometry and input capture; not Minecraft acceptance. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {RACK_SELECTION_BOX,rackAimHit,rackTouchHit,captureRackHit} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_aim_hit.js';
import {ADVANCED_RACK_BLOCK_ID} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2746_advanced_rack_core.js';
import {rackSlotAtHit} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_rack_quick_pick.js';
const scripts=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const near=(a,b)=>assert.ok(a&&['x','y','z'].every(axis=>Math.abs(a[axis]-b[axis])<1e-9),JSON.stringify({actual:a,expected:b}));
const dimension={id:'minecraft:overworld'};
const target=(location={x:320,y:-59,z:319})=>({typeId:ADVANCED_RACK_BLOCK_ID,dimension,location});
function player(block,point={x:.5,y:.6744117737,z:.0625},mode='KeyboardAndMouse',hotbar){
 return {dimension,inputInfo:{lastInputModeUsed:mode,touchOnlyAffectsHotbar:hotbar},
  getHeadLocation:()=>({x:block.location.x+point.x,y:block.location.y+point.y,z:block.location.z-2}),
  getViewDirection:()=>({x:0,y:0,z:1}),
  getBlockFromViewDirection(){throw Error('Must not redirect actual event target');}};
}
test('reviewed square selection box and all cardinal transforms match the shipped asset',()=>{
 const def=JSON.parse(fs.readFileSync(new URL('../blocks/advanced_rack_block.json',scripts)))['minecraft:block'];
 assert.deepEqual(RACK_SELECTION_BOX,def.components['minecraft:selection_box']);
 const transforms=def.permutations.filter(p=>p.components['minecraft:transformation']);assert.equal(transforms.length,4);
 for(const p of def.permutations){assert.equal(p.components['minecraft:selection_box'],undefined);const t=p.components['minecraft:transformation'];if(!t)continue;
  assert.deepEqual(Object.keys(t),['rotation']);assert.equal(t.rotation[0],0);assert.equal(t.rotation[2],0);assert.equal(t.rotation[1]%90,0);
 }
 assert.equal(fs.readFileSync(new URL('rack_aim_hit.js',scripts),'utf8'),fs.readFileSync(new URL('rack_aim_hit.js',import.meta.url),'utf8'));
});
test('all six surfaces intersect at reviewed selection-box boundaries',()=>{
 const lo={x:1/16,y:5/16,z:1/16},hi={x:15/16,y:14/16,z:15/16};
 for(const axis of ['x','y','z'])for(const sign of [-1,1]){
  const hit={x:.5,y:.6,z:.5};hit[axis]=(sign<0?lo:hi)[axis];
  const origin={...hit,[axis]:hit[axis]+sign*2},direction={x:0,y:0,z:0};direction[axis]=-sign;
  near(rackAimHit(origin,direction),hit);
 }
});
test('parallel, backwards, zero, nonfinite and missing rays fail closed',()=>{
 for(const [origin,direction] of [[{x:2,y:.7,z:2},{x:0,y:0,z:1}],[{x:.5,y:.7,z:-2},{x:0,y:0,z:-1}],[{x:.5,y:.7,z:-2},{x:0,y:0,z:0}],[{x:.5,y:.7,z:-2},{x:NaN,y:0,z:1}],[{x:Infinity,y:.7,z:-2},{x:0,y:0,z:1}],[undefined,{x:0,y:0,z:1}]])assert.equal(rackAimHit(origin,direction),undefined);
 near(rackAimHit({x:.5,y:.7,z:.5},{x:0,y:0,z:1}),{x:.5,y:.7,z:.5});
});
test('all saved slot indices survive all facings, both rows and all world sign combinations',()=>{
 for(const x of [-320,320])for(const y of [-59,64])for(const z of [-319,319])for(const facing of ['north','east','south','west'])for(let slot=0;slot<9;slot++){
  const count=slot<5?5:4,cell=slot<5?slot:slot-5,u=1/16+(cell+.5)*(14/16)/count,v=slot<5?12/16:6/16;
  const local=facing==='north'?{x:u,y:v,z:1/16}:facing==='south'?{x:1-u,y:v,z:15/16}:facing==='east'?{x:15/16,y:v,z:u}:{x:1/16,y:v,z:1-u};
  const out=facing==='north'?{x:0,y:0,z:-1}:facing==='south'?{x:0,y:0,z:1}:facing==='east'?{x:1,y:0,z:0}:{x:-1,y:0,z:0};
  const block=target({x,y,z}),p=player(block);p.getHeadLocation=()=>({x:x+local.x+2*out.x,y:y+local.y,z:z+local.z+2*out.z});p.getViewDirection=()=>({x:-out.x,y:0,z:-out.z});
  const result=captureRackHit(p,block,'North',{x:1-local.x,y:1-local.y,z:1-local.z});near(result.point,local);assert.equal(rackSlotAtHit(facing,result.point),slot,`${x},${y},${z}/${facing}/${slot}`);
 }
});
test('G77 native negative-Y hit selects upper slot via independent ray, never its mirrored event row',()=>{
 const b=target(),p=player(b),native={x:.5001525879,y:.3255882263,z:.0625};
 assert.equal(rackSlotAtHit('north',native),7);
 const result=captureRackHit(p,b,'North',native);assert.equal(result.source,'eye_ray');assert.equal(rackSlotAtHit('north',result.point),2);
 near(result.origin,{x:.5,y:.6744117737,z:-2});near(result.direction,{x:0,y:0,z:1});
});
test('direct touch keeps the off-crosshair event point; crosshair Touch uses the eye ray',()=>{
 const b=target(),native={x:.5,y:.6,z:.0625};
 for(const [mode,hotbar,want,source] of [['Touch',false,7,'direct_touch'],['Touch',true,2,'eye_ray'],['Touch',undefined,2,'eye_ray'],['Gamepad',false,2,'eye_ray'],[undefined,false,2,'eye_ray']]){
  const result=captureRackHit(player(b,undefined,mode,hotbar),b,'North',native);assert.equal(result.source,source);assert.equal(rackSlotAtHit('north',result.point),want);
 }
});
test('direct-touch decode preserves all six surfaces across negative world axes',()=>{
 for(const x of [-3,3])for(const y of [-3,3])for(const z of [-3,3])for(const [face,axis,normal] of [['West','x',1/16],['East','x',15/16],['Down','y',5/16],['Up','y',14/16],['North','z',1/16],['South','z',15/16]]){
  const location={x,y,z},local={x:.3,y:.7,z:.4};local[axis]=normal;
  const raw=Object.fromEntries(['x','y','z'].map(a=>[a,location[a]<0?1-local[a]:local[a]]));near(rackTouchHit(location,face,raw),local);
 }
});
test('invalid direct-touch coordinates or unknown face never substitute the crosshair ray',()=>{
 const b=target(),p=player(b,undefined,'Touch',false);
 for(const [face,hit] of [['North',undefined],['North',{x:NaN,y:.4,z:.0625}],['North',{x:.5,y:.95,z:.0625}],['invalid',{x:.5,y:.4,z:.0625}]]){
  const result=captureRackHit(p,b,face,hit);assert.equal(result.point,undefined);assert.equal(result.reason,'invalid_touch_hit');assert.ok(result.aimed);
 }
});
test('known direct touch works without eye APIs; every crosshair path rejects absent or missed eye rays',()=>{
 const b=target(),native={x:.5,y:.3255882263,z:.0625};
 const touch={dimension,inputInfo:{lastInputModeUsed:'Touch',touchOnlyAffectsHotbar:false}};assert.equal(rackSlotAtHit('north',captureRackHit(touch,b,'North',native).point),2);
 for(const p of [{dimension},{dimension,inputInfo:{lastInputModeUsed:'Touch',touchOnlyAffectsHotbar:true}},{...player(b),getHeadLocation(){throw Error('unavailable');}},{...player(b),getViewDirection:()=>({x:0,y:0,z:-1})}]){
  const result=captureRackHit(p,b,'North',native);assert.equal(result.point,undefined);assert.equal(result.reason,'missing_or_missed_ray');
 }
});
test('invalid event targets, wrong dimensions and fractional block positions cannot redirect to a rack',()=>{
 const b=target(),p=player(b),native={x:.5,y:.3255882263,z:.0625};
 for(const other of [undefined,{...b,typeId:'minecraft:stone'},{...b,location:{x:320.5,y:-59,z:319}},{...b,dimension:{id:'minecraft:nether'}}])assert.equal(captureRackHit(p,other,'North',native).point,undefined);
});
test('inputInfo failure still permits a valid ray and returned snapshots do not alias engine vectors',()=>{
 const b=target(),p=player(b),head=p.getHeadLocation(),direction=p.getViewDirection();p.getHeadLocation=()=>head;p.getViewDirection=()=>direction;Object.defineProperty(p,'inputInfo',{get(){throw Error('unavailable');}});
 const result=captureRackHit(p,b,'North',undefined);assert.equal(rackSlotAtHit('north',result.point),2);head.y=999;direction.z=-1;near(result.direction,{x:0,y:0,z:1});near(result.origin,{x:.5,y:.6744117737,z:-2});
});
