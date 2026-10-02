import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {planDragonDamage,dragonHealthGain} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/dragon_health_core.js';
test('two same-tick hits reserve one bounded remainder without read-only writes',()=>{
 const first=planDragonDamage(2,1.5),second=planDragonDamage(2,3,first.pending);assert.equal(first.absorbed,1.5);assert.equal(second.absorbed,.5);assert.equal(second.remaining,2.5);assert.equal(planDragonDamage(0,3).absorbed,0);
});
test('depleted remainder persists as zero until expiry; refresh never restores it',()=>{
 const source=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/main.js','utf8'),ctx={DRAGON_POOL_KEY:'pool'};
 vm.runInNewContext(source.match(/function setDragonPool\(entity,value\)\{[^\n]+/)[0]+'\nthis.write=setDragonPool',ctx);const data=new Map(),store={setDynamicProperty:(k,v)=>v===undefined?data.delete(k):data.set(k,v),getDynamicProperty:k=>data.get(k)};
 ctx.write(store,0);assert.equal(store.getDynamicProperty('pool'),0);assert.equal(store.getDynamicProperty('pool')===undefined,false);ctx.write(store,undefined);assert.equal(data.size,0);
});
test('new application heals native gain once, refresh heals zero, upgrade heals only four',()=>{assert.equal(dragonHealthGain(undefined,0),4);assert.equal(dragonHealthGain(undefined,1),8);assert.equal(dragonHealthGain(0,0),0);assert.equal(dragonHealthGain(0,1),4);assert.equal(dragonHealthGain(1,0),0)});
