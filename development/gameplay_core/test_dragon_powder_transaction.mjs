// Fault injection into the actual production function. This is not a Minecraft player test.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {dragonPowderCount,knifeDamagePlan} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/dragon_powder_core.js';
import {isKitchenKnifeStack} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2710_chicken_acquisition_core.js';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/dragon_powder_runtime.js',import.meta.url),'utf8');
const body=source.slice(source.indexOf('function enchantment('),source.indexOf('world.beforeEvents.')).replace('export function','function')+'\nthis.execute=shaveDragonPowder;';
class Stack{
 constructor(id,amount=1){this.typeId=id;this.amount=amount;this.maxAmount=id.endsWith('knife')?1:64;this.damage=2;}
 clone(){return Object.assign(new Stack(this.typeId,this.amount),this);}
 getTags(){return this.typeId.endsWith('knife')?['kaleidoscope_cookery:kitchen_knife']:[];}
 getComponent(id){if(id==='minecraft:durability'){const self=this;return {get damage(){return self.damage},set damage(x){self.damage=x},maxDurability:10}};if(id==='minecraft:enchantable')return {getEnchantment:()=>({level:0})};}
 isStackableWith(other){return this.typeId===other.typeId;}
}
let cases=0;
for(const mode of ['normal','hand_failure','output_failure','drop','drop_failure','creative','break']){
 const knife=new Stack('kaleidoscope_cookery:iron_kitchen_knife');if(mode==='break')knife.damage=9;
 const rows=[knife,mode.startsWith('drop')?new Stack('minecraft:stone',64):undefined];let drops=[];
 const container={size:2,getItem:i=>rows[i]?.clone(),setItem(i,value){rows[i]=value?.clone();if(mode==='output_failure'&&i===1&&value?.typeId.endsWith('dragon_egg_powder'))throw Error('injected partial output write');}};
 const player={selectedSlotIndex:0,location:{x:0,y:0,z:0},dimension:{spawnItem(s){if(mode==='drop_failure')throw Error('injected spawn rejection');const entity={stack:s,remove(){drops=drops.filter(x=>x!==entity)}};drops.push(entity);return entity;}},playSound(){}};
 const context=vm.createContext({ItemStack:Stack,POWDER:'kaleidoscope_grilling:dragon_egg_powder',isKitchenKnifeStack,commitSteps,dragonPowderCount,knifeDamagePlan,isCreative:()=>mode==='creative',playerInventory:()=>container,captureWritableHand(){return {before:rows[0].clone(),write(s){rows[0]=s?.clone();if(mode==='hand_failure'&&s?.damage===3)throw Error('injected hand write')}}}});
 vm.runInContext(body,context);
 const failed=mode.endsWith('failure');
 if(failed)assert.throws(()=>context.execute(player,'main',()=>0));else assert.equal(context.execute(player,'main',()=>0),true);
 if(failed){assert.equal(rows[0].damage,2);assert.equal(drops.length,0);if(!mode.startsWith('drop'))assert.equal(rows[1],undefined);}
 else if(mode==='break')assert.equal(rows[0],undefined);
 else assert.equal(rows[0].damage,mode==='creative'?2:3);
 if(mode==='normal'||mode==='creative'||mode==='break')assert.equal(rows[1].amount,1);
 if(mode==='drop')assert.equal(drops[0].stack.amount,1);
 cases++;
}
assert.ok(!/event\.cancel\s*=/.test(source),'must preserve native dragon egg interaction');
console.log(`PASS ${cases} actual dragon-powder transaction/fault cases; native client input remains untested`);
