import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const plan=JSON.parse(readFileSync(new URL('./a2755_fortress_loot_plan.json',import.meta.url),'utf8'));
assert.equal(plan.version,'A2.7.55');
assert.equal(plan.mojang_baseline.version,'1.26.50.4');
assert.equal(plan.vanilla_table.path,'behavior_pack/loot_tables/chests/nether_bridge.json');
assert.match(plan.vanilla_table.sha,/^[0-9a-f]{40}$/);
assert.deepEqual(plan.bonus,{
 chance:0.65,rolls:{min:1,max:2},
 item:'kaleidoscope_grilling:houttuynia',
 count:{min:1,max:3}
});
console.log('A2.7.55 Fortress Houttuynia Loot plan: PASS');
