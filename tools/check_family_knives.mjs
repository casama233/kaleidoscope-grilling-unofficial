import assert from 'node:assert/strict';
import fs from 'node:fs';
import {isKitchenKnife,KITCHEN_KNIVES,KITCHEN_KNIFE_TAG} from '../projects/grilling/gameplay_core/behavior_pack/scripts/a2710_chicken_acquisition_core.js';
for(const id of KITCHEN_KNIVES)assert.equal(isKitchenKnife(id,[]),true);
assert.equal(isKitchenKnife('kaleidoscope_end:dragon_tooth_knife',[KITCHEN_KNIFE_TAG]),true);
assert.equal(isKitchenKnife('kaleidoscope_nether:primitive_machete',[KITCHEN_KNIFE_TAG]),true);
assert.equal(isKitchenKnife('other:new_knife',[KITCHEN_KNIFE_TAG]),true);
assert.equal(isKitchenKnife('other:kitchen_knife',[]),false);
assert.equal(isKitchenKnife('minecraft:diamond_sword',[]),false);
assert.equal(isKitchenKnife('minecraft:diamond_sword',['not_'+KITCHEN_KNIFE_TAG]),false);
for(const name of ['a2710_chicken_acquisition_runtime.js','a2712_remaining_knife_drops_runtime.js']){
 const text=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/'+name,'utf8');
 assert.ok(text.includes('isKitchenKnifeStack(weapon)'));
}
for(const name of ['a2710_chicken_acquisition_core.js','a2710_chicken_acquisition_runtime.js','a2712_remaining_knife_drops_runtime.js','a279_beef_board_runtime.js','a2736_typed_oil_pot_block_runtime.js','a2739_cookery_oil_pot_block_adapter.js']){
 assert.equal(fs.readFileSync('development/gameplay_core/'+name,'utf8'),fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/'+name,'utf8'));
}
for(const name of ['a279_beef_board_runtime.js','a2736_typed_oil_pot_block_runtime.js','a2739_cookery_oil_pot_block_adapter.js','a2710_chicken_acquisition_runtime.js']){
 const text=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/'+name,'utf8');
 assert.ok(!/world\.setDynamicProperty|spawnItem.*CHICKEN_SKIN|setPermutation|setType\(/.test(text),name);
 assert.ok(!/kc_station:|kc_oilpot:/.test(text),name);
}
console.log('PASS: 10 pure knife/tag cases, actual call-site wiring, paired sources, no private station writes; no player or ItemStack mock.');
