import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import vm from 'node:vm';
import {premiumOilParticles,premiumOilPotParticles,premiumOilPotInRange} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_ambient_core.js';
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
test('oil-pot bursts use the original spout and always pair flame with lava',()=>{
 assert.deepEqual(premiumOilPotParticles(draws([.2])),[]);
 const particles=premiumOilPotParticles(draws([.19,0,.5]));
 assert.equal(particles.length,2);assert.deepEqual(particles[0].offset,[.42,.72,.5]);
 assert.deepEqual(particles[0].velocity,[0,.14,0]);assert.deepEqual(particles[1].velocity,[0,.11,0]);
});
test('oil-pot runtime samples nearby clients independently and ignores unloaded or empty pots',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_pot_ambient_runtime.js',import.meta.url),'utf8').replace(/^import .*;$/gm,'');
 const station={dimensionId:'minecraft:overworld',x:-1,y:64,z:0},calls=[];
 const listener=(id,x,y=64,dimensionId=station.dimensionId)=>({id,location:{x,y,z:0},dimension:{id:dimensionId}});
 // Range uses blockPosition (including negative coordinates), not radial distance.
 const nearby=[listener('a',7.99,68.99),listener('b',-9)],players=[...nearby,listener('far',8),listener('above',0,69),listener('other',0,64,'minecraft:nether')];
 let tick,period,loaded=true,state={type:'premium_chili',count:1},draw=0;
 const dimension={getBlock:()=>loaded?{typeId:'kaleidoscope_cookery:oil_pot'}:undefined};
 const context=vm.createContext({system:{runInterval(fn,n){tick=fn;period=n}},world:{getAllPlayers:()=>players,getDimension:()=>dimension},
  currentPlacedOilPotCandidates:()=>[station],HOST_BLOCK_ID:'kaleidoscope_cookery:oil_pot',readPlacedOilPotState:()=>state,premiumOilPotInRange,
  premiumOilPotParticles:()=>[{sample:++draw}],emitParticles:(player,origin,particles)=>calls.push({player:player.id,origin,particles})});
 vm.runInContext(source,context);assert.equal(period,8);tick();
 assert.deepEqual(calls.map(x=>x.player),['a','b']);assert.notEqual(calls[0].particles[0].sample,calls[1].particles[0].sample);
 state={type:'premium_chili',count:0};tick();loaded=false;state={type:'premium_chili',count:1};tick();
 assert.equal(calls.length,2);
});
