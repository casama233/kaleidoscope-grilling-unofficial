import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const plan=JSON.parse(readFileSync(new URL('./a2754_village_loot_plan.json',import.meta.url),'utf8'));
let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('Mojang vanilla baseline matches the target Bedrock engine family',()=>{
 assert.equal(plan.version,'A2.7.54');
 assert.equal(plan.mojang_baseline.repo,'Mojang/bedrock-samples');
 assert.equal(plan.mojang_baseline.commit,'46ba6ea985fb5a92d79a9419198f10dda14c199d');
 assert.equal(plan.mojang_baseline.version,'1.26.50.4');
});

t('exactly fifteen real village chest tables are wrapped',()=>{
 assert.equal(plan.village_tables.length,15);
 const names=plan.village_tables.map(x=>x[0]);
 assert.equal(new Set(names).size,15);
 assert.equal(names.includes('village_bundle.json'),false);
 for(const [name,sha] of plan.village_tables){
  assert.match(name,/^village_[a-z_]+\.json$/);
  assert.match(sha,/^[0-9a-f]{40}$/);
 }
});

t('Pepper bonus preserves two independent Java loot pools',()=>{
 assert.deepEqual(plan.bonus.pepper,{
  item:'kaleidoscope_grilling:sichuan_pepper',chance:0.4,min:3,max:10
 });
 assert.deepEqual(plan.bonus.sapling,{
  item:'kaleidoscope_grilling:pepper_sapling',chance:0.2,count:1
 });
});

console.log('A2.7.54 Village Pepper Loot plan: '+n+'/'+n);
