import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {test} from 'node:test';
import {TimedWorkQueue} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/timed_work_queue.js';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a23_oil_world.js',import.meta.url),'utf8');
// Execute the real cache/recovery functions without subscribing native events.
const start=source.indexOf('let registryCache'),end=source.indexOf('function loadReg');
function fixture(){
 const context=vm.createContext({TimedWorkQueue,system:{currentTick:70}});
 vm.runInContext(source.slice(start,end)+`;this.api={restoreRegistryCache,addClaims,sourceIndex,sourceSlots,claims,claimCells,get cache(){return registryCache},get queue(){return dueQueue}}`,context);
 return context.api;
}
test('rollback replaces all derived source, slot, ownership and scheduled-work state',()=>{
 const api=fixture();
 const old={k:'old',cells:['shared','old-only'],nextTick:80};
 api.restoreRegistryCache([old]);
 api.sourceIndex.set('failed',{k:'failed'});api.sourceSlots.set('failed',1);
 api.addClaims({k:'failed',cells:['shared','failed-only']});api.queue.schedule('failed',70);
 api.restoreRegistryCache([{...old,cells:[...old.cells]}]);
 assert.deepEqual([...api.sourceIndex.keys()],['old']);assert.equal(api.sourceSlots.size,1);assert.equal(api.sourceSlots.get('old'),0);
 assert.deepEqual([...api.claims.get('shared')],['old']);assert.equal(api.claims.has('failed-only'),false);
 assert.equal(api.claimCells.has('failed'),false);assert.deepEqual([...api.queue.take(70,8)],[]);
 assert.deepEqual([...api.queue.take(80,8)],['old']);assert.equal(api.cache.length,1);
});
test('empty pre-transaction registry removes every failed source and future retry',()=>{
 const api=fixture();api.restoreRegistryCache([{k:'failed',cells:['cell'],nextTick:100}]);
 api.restoreRegistryCache([]);assert.equal(api.sourceIndex.size,0);assert.equal(api.sourceSlots.size,0);
 assert.equal(api.claims.size,0);assert.equal(api.claimCells.size,0);assert.equal(api.queue.size,0);
 assert.deepEqual([...api.queue.take(1000,8)],[]);
});
