import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {advancedRackToolVisuals,ADVANCED_RACK_HOOK_X} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/advanced_rack_visual_core.js';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/station_contents_visual_runtime.js',import.meta.url),'utf8');
function sync(rows,oldKeys=[]){
 const out=[],discarded=[],parts=new Map(oldKeys.map(k=>[k,{}]));
 const row={dimensionId:'test',parts};
 const block={typeId:'kaleidoscope_grilling:advanced_rack_block',x:0,y:0,z:0};
 const read=[];
 const ctx={rememberStationVisual(){},targets:new Map([['rack',row]]),key:()=> 'rack',peekStationContainer:()=>({getItem(i){read.push(i);return rows[i]}}),advancedRackToolVisuals,pose:(_b,x,y,z)=>({x,y,z}),render:(_r,_b,key,stack,at,mode)=>{if(stack)out.push({key,stack,at,mode})},discard:(_r,k)=>{discarded.push(k);parts.delete(k)},clear(){},work:{remove(){}}};
 const start=source.indexOf('export function syncStationContentsVisual('),end=source.indexOf('\nfunction index()',start);
 assert.ok(start>=0&&end>start);vm.runInNewContext(source.slice(start,end).replace('export ',''),ctx);
 ctx.syncStationContentsVisual(block,[{dimensionId:'test',x:0,y:0,z:0}]);return {out,discarded,read};
}
test('all nine occupied slots render only the first three tool slots',()=>{
 const rows=Array.from({length:9},(_,i)=>({typeId:'fixture:'+i})),f=sync(rows);
 assert.deepEqual(f.out.map(x=>x.key),['rack/5','rack/6','rack/7']);
 assert.equal(rows[8].typeId,'fixture:8');
});
test('all tool occupancy masks compress onto source hook positions without changing inventory',()=>{
 assert.deepEqual(ADVANCED_RACK_HOOK_X,[-.284,0,.278]);
 for(let mask=0;mask<16;mask++){
  const rows=Array(9);for(let i=0;i<4;i++)if(mask&(1<<i))rows[5+i]={typeId:'fixture:'+i};
  const before=rows.slice(),expected=[5,6,7,8].filter(i=>rows[i]).slice(0,3),plan=advancedRackToolVisuals(i=>rows[i]),f=sync(rows);
  assert.deepEqual(plan.map(x=>x.slot),expected);assert.deepEqual(plan.map(x=>x.hook),expected.map((_,i)=>i));
  assert.deepEqual(f.out.map(x=>x.key),expected.map(i=>'rack/'+i));assert.deepEqual(f.out.map(x=>x.at.x),expected.map((_,i)=>ADVANCED_RACK_HOOK_X[i]));
  assert.deepEqual(rows,before);for(let i=0;i<plan.length;i++)assert.equal(plan[i].stack,rows[expected[i]]);
 }
});
test('upper spice-level appearance never spawns an additional equipped item',()=>{
 const rows=Array.from({length:5},(_,i)=>({typeId:'fixture:seasoning_'+i}));
 assert.equal(sync(rows).out.length,0);
 const read=[];advancedRackToolVisuals(i=>{read.push(i);return rows[i]});assert.deepEqual(read,[5,6,7,8]);
});
test('slot eight is visible when fewer than three earlier tools are occupied',()=>{
 const rows=Array(9);rows[6]={typeId:'fixture:first'};rows[8]={typeId:'fixture:last'};
 const f=sync(rows);assert.deepEqual(f.out.map(x=>x.key),['rack/6','rack/8']);assert.deepEqual(f.out.map(x=>x.at.x),[-.284,0]);
});
test('old upper and fourth-tool helpers retire; storage items stay intact',()=>{
 const rows=Array.from({length:9},(_,i)=>({typeId:'fixture:'+i})),keys=Array.from({length:9},(_,i)=>'rack/'+i),f=sync(rows,keys);
 assert.deepEqual(f.discarded,['rack/0','rack/1','rack/2','rack/3','rack/4','rack/8']);assert.equal(rows.filter(Boolean).length,9);
});
test('no tools produces no visual rows',()=>assert.deepEqual(advancedRackToolVisuals(()=>undefined),[]));
