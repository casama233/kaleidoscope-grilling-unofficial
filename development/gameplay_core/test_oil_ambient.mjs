import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import vm from 'node:vm';
import {premiumOilParticles} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_ambient_core.js';
const draws=values=>()=>{assert.ok(values.length);return values.shift()};
test('Java one-in-five lava chance, half flame chance, positions and velocities',()=>{
 assert.deepEqual(premiumOilParticles(draws([.2])),[]);
 const both=premiumOilParticles(draws([.19,0,.5,1,.49]));
 assert.equal(both.length,2);assert.deepEqual(both[0].offset,[.15,.85,.85]);
 assert.deepEqual(both[0].velocity,[0,.05,0]);assert.deepEqual(both[1].velocity,[0,.035,0]);
 assert.equal(premiumOilParticles(draws([0,.5,.5,.5,.5])).length,1);
});
test('unchanged oil cells perform zero native permutation writes; changed level still writes',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a23_oil_world.js',import.meta.url),'utf8');
 let writes=0,level=2;const block={typeId:'premium',permutation:{getState:()=>level},setPermutation(p){writes++;this.typeId=p.id;level=p.states['kaleidoscope_grilling:level']}};
 const ctx=vm.createContext({OIL_TYPES:{premium_chili:{block:'premium'}},BlockPermutation:{resolve:(id,states)=>({id,states})}});
 vm.runInContext(source.slice(source.indexOf('function setOil('),source.indexOf('function canFlowInto('))+';this.setOil=setOil;',ctx);
 for(let i=0;i<512;i++)assert.equal(ctx.setOil(block,'premium_chili',2),true);
 assert.equal(writes,0);assert.equal(ctx.setOil(block,'premium_chili',3),true);assert.equal(writes,1);assert.equal(level,3);
 block.typeId='minecraft:air';assert.equal(ctx.setOil(block,'premium_chili',3),true);assert.equal(writes,2);
 block.setPermutation=()=>{throw Error('unloaded')};assert.equal(ctx.setOil(block,'premium_chili',4),false);
});
