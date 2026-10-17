import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {test} from 'node:test';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a23_oil_world.js',import.meta.url),'utf8');
test('contained flow reuses native block reads within a cycle and observes changes next cycle',()=>{
 const cells=new Map(),reads=new Map();let heights=0;
 const key=(d,x,y,z)=>`${d}|${x}|${y}|${z}`;
 const dim={get heightRange(){heights++;return {min:-64}},getBlock(p){const k=key('overworld',p.x,p.y,p.z);reads.set(k,(reads.get(k)??0)+1);if(!cells.has(k))cells.set(k,{typeId:p.y<81||Math.abs(p.x)>3||Math.abs(p.z)>3?'minecraft:stone':'minecraft:air',lvl:0});return cells.get(k)}};
 const row={d:'overworld',x:0,y:81,z:0,k:key('overworld',0,81,0),type:'test',cells:[]};
 dim.getBlock({x:0,y:81,z:0}).typeId='oil';reads.clear();
 const context=vm.createContext({world:{getDimension:()=>dim},OIL_TYPES:{test:{block:'oil'}},posKey:key,FLOW_CELL_BUDGET:512,HORIZ:[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]],level:b=>b.lvl,canFlowInto:b=>b&&['oil','minecraft:air'].includes(b.typeId),setOil:(b,t,l)=>{b.typeId='oil';b.lvl=l},sourceKeys:()=>new Map([[row.k,row]]),claimedByOther:()=>false,clearCells:()=>{}});
 vm.runInContext(source.slice(source.indexOf('function compute('),source.indexOf('function faceTarget'))+';this.compute=compute;',context);
 assert.equal(context.compute(row,[row]),true);assert.equal(row.cells.length,48);assert.equal(heights,1);assert.ok([...reads.values()].every(n=>n===1));
 const target=key('overworld',1,81,0);cells.get(target).typeId='minecraft:stone';reads.clear();
 assert.equal(context.compute(row,[row]),true);assert.equal(row.cells.length,47);assert.ok(!row.cells.includes(target));assert.equal(heights,2);assert.ok([...reads.values()].every(n=>n===1));assert.equal(cells.get(target).typeId,'minecraft:stone');
});
