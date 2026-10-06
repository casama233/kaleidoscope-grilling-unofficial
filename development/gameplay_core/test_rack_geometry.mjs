/** Resource/layout assertions only. Actual block bone visibility requires client QA. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {RACK_SEASONING_X,RACK_TOOL_X,RACK_OCCUPANCY_STATE} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/advanced_rack_layout.js';
const root=new URL('../../projects/grilling/gameplay_core/',import.meta.url);
const read=path=>JSON.parse(fs.readFileSync(new URL(path,root),'utf8'));
test('all established rack geometries have matching four fixed hooks and five shelf cells',()=>{
 for(let level=0;level<5;level++){
  const geometry=read(`resource_pack/models/blocks/advanced_rack_${level}.geo.json`)['minecraft:geometry'][0];
  assert.equal(geometry.description.identifier,`geometry.kg_a1.advanced_rack_${level}`);
  assert.equal(geometry.description.texture_width,32);assert.equal(geometry.description.texture_height,32);
  const bones=new Map(geometry.bones.map(b=>[b.name,b]));assert.equal(bones.size,geometry.bones.length);
  for(const bone of bones.values())if(bone.parent)assert.ok(bones.has(bone.parent));
  for(let slot=0;slot<4;slot++){
   assert.ok(bones.has(`rack_tool_hook_${slot}`));const part=bones.get(`rack_tool_part_${slot}_0`),c=part.cubes[0];
   assert.equal(part.parent,`rack_tool_hook_${slot}`);assert.ok(Math.abs((c.origin[0]+c.size[0]/2)/16-RACK_TOOL_X[slot])<1e-9);
  }
  assert.equal([...bones.keys()].filter(x=>/^rack_tool_hook_/.test(x)).length,4);
  for(let slot=0;slot<5;slot++){
   const jar=bones.get(`rack_seasoning_${slot}`),body=jar.cubes[0];assert.equal(jar.cubes.length,4);
   assert.ok(Math.abs((body.origin[0]+body.size[0]/2)/16-RACK_SEASONING_X[slot])<1e-9);
  }
  // Prevent old compacted hook/jar groups from being layered under new cells.
  assert.equal([...bones.keys()].filter(x=>/^instance_0_(source_[567]_mixed|element_(7|2[6-9]|3\d|4\d)_)/.test(x)).length,0);
 }
});
test('block bone visibility represents each of32 exact slot masks for every saved spice variant',()=>{
 const block=read('behavior_pack/blocks/advanced_rack_block.json')['minecraft:block'];
 assert.deepEqual(block.description.states[RACK_OCCUPANCY_STATE],Array.from({length:32},(_,i)=>i));
 assert.deepEqual(block.description.states['kaleidoscope_grilling:spice_level'],[0,1,2,3,4]);
 const geometries=[block.components['minecraft:geometry'],...block.permutations.slice(0,5).map(p=>p.components['minecraft:geometry'])];
 for(const geometry of geometries)for(let mask=0;mask<32;mask++)for(let slot=0;slot<5;slot++){
  const expression=geometry.bone_visibility[`rack_seasoning_${slot}`];
  const visible=vm.runInNewContext(expression,{math:{floor:Math.floor},q:{block_state:state=>{assert.equal(state,RACK_OCCUPANCY_STATE);return mask;}}});
  assert.equal(visible,!!(mask&(1<<slot)));
 }
});
