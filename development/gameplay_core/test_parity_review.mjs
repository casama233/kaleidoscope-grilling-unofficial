import {normalizePublicFood,readPublicFood,writePublicFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import {stationProjection,registerStationProjection} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/station_projection_core.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {TimedWorkQueue} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/timed_work_queue.js';
import {VisualTargetQueue} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/visual_target_queue.js';
import {activeEffects,milkEffects,effectPayload,FX_KEY} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/effect_lifecycle_core.js';
import {normalizeConfig,configValue} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/server_config_core.js';
import {seasoningLore,creatorLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
const scriptRoot='projects/grilling/gameplay_core/behavior_pack/scripts/';
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport /g,'');
test('milk cures every active grilling effect except Java uncurable poisoning',()=>{
 const input={invincible:{until:500,amp:0},dragon_blood:{until:500,amp:1},numb:{until:500,amp:0},heavy_metal:{until:500,amp:0},heavy_metal_poisoning:{until:700,amp:0},warmth:{until:20,amp:0}};
 assert.deepEqual(milkEffects(input,100),{heavy_metal_poisoning:{until:700,amp:0}});assert.deepEqual(milkEffects(input,701),{});assert.equal(effectPayload({},100),undefined);
});
test('shared effect runtime avoids empty/unchanged writes and preserves extended duration',()=>{
 const dp=new Map();let writes=0,reads=0,tick=1,time=100;
 const entity={getDynamicProperty(k){reads++;return dp.get(k)},setDynamicProperty(k,v){writes++;if(v===undefined)dp.delete(k);else dp.set(k,v)}};
 const context={world:{getAbsoluteTime:()=>time},system:{get currentTick(){return tick}},activeEffects,effectPayload,milkEffects,FX_KEY};
 vm.runInNewContext(strip(fs.readFileSync(scriptRoot+'effect_state_runtime.js','utf8'))+';this.api={readEffects,writeEffects,clearEffects}',context);
 for(let i=0;i<20;i++)context.api.writeEffects(entity,context.api.readEffects(entity));assert.equal(writes,0);assert.equal(reads,1);
 context.api.writeEffects(entity,{dragon_blood:{until:200,amp:0},heavy_metal_poisoning:{until:400,amp:0}});assert.equal(writes,1);
 context.api.writeEffects(entity,context.api.readEffects(entity));assert.equal(writes,1);
 context.api.clearEffects(entity,{milk:true});assert.deepEqual(JSON.parse(dp.get(FX_KEY)),{heavy_metal_poisoning:{until:400,amp:0}});
 context.api.clearEffects(entity);assert.equal(dp.get(FX_KEY),undefined);tick++;time=500;assert.equal(Object.keys(context.api.readEffects(entity)).length,0);
});
test('deadline queue orders work, replaces keys and cancels without visiting future keys',()=>{
 const q=new TimedWorkQueue();for(let i=0;i<1000;i++)q.schedule('future'+i,5000+i);q.schedule('urgent',2);q.schedule('cancel',1);q.cancel('cancel');q.schedule('urgent',0);
 assert.deepEqual(q.take(0,8),['urgent']);assert.deepEqual(q.take(4999,8),[]);assert.equal(q.size,1000);assert.deepEqual(q.take(5007,8),Array.from({length:8},(_,i)=>'future'+i));
});
test('dirty nearby station updates before 1000 far saved stations; idle world visits none',()=>{
 const q=new VisualTargetQueue();for(let i=0;i<1000;i++)q.add('far'+i,{dimensionId:'overworld',location:{x:10000+i,y:0,z:0}});
 for(let i=0;i<20;i++)q.add('near'+i,{dimensionId:'overworld',location:{x:i,y:0,z:0}});
 q.observe([{dimensionId:'overworld',x:0,y:0,z:0}]);q.take(8);q.mark('near19');assert(q.take(8).includes('near19'));assert(q.take(8).every(k=>k.startsWith('near')));
 q.observe([]);for(let i=0;i<8;i++)q.take(8);assert.deepEqual(q.take(8),[]);assert.equal(q.dirty.size,0);
});
test('continuous edits cannot starve fair refresh with a bounded work budget',()=>{
 const q=new VisualTargetQueue();for(let i=0;i<20;i++)q.add(String(i),{dimensionId:'overworld',location:{x:i,y:0,z:0}});q.observe([{dimensionId:'overworld',x:0,y:0,z:0}]);
 const seen=new Set();for(let i=0;i<40;i++){q.mark('0');for(const k of q.take(2))seen.add(k)}assert.equal(seen.size,20);
});
test('configuration accepts meaningful limits and rejects invalid/unknown values',()=>{
 assert.equal(normalizeConfig({saturationMultiplier:2}).saturationMultiplier,2);assert.equal(configValue('fullHungerEating','false'),false);assert.equal(configValue('contentsHelpers','4096'),4096);
 for(const [k,v] of [['contentsHelpers',0],['contentsTargetsPerTick',100],['saturationMultiplier',Infinity],['fullHungerEating','yes'],['unknown',1]])assert.throws(()=>configValue(k,v));
});
test('runtime lore uses language keys rather than fixed language text',()=>{
 assert.equal(seasoningLore(16,8,{pending:true}).length,3);assert.equal(creatorLore('name').with[0],'name');
 for(const lang of ['en_US','zh_TW','zh_CN']){const text=fs.readFileSync('projects/grilling/gameplay_core/resource_pack/texts/'+lang+'.lang','utf8');for(const line of [...seasoningLore(1,2,{missingBase:true}),creatorLore('name')])assert(text.includes(line.translate+'='));}
});

test('public native variant survives heat metadata rewrites and rejects invalid data',()=>{
 const stack={lore:[],getRawLore(){return this.lore},setLore(v){this.lore=v}};
 writePublicFood(stack,{v:1,hotUntil:1201,seasoning:[],nativeVariant:7});const state=readPublicFood(stack).state;
 writePublicFood(stack,{...state,hotUntil:1200});assert.equal(readPublicFood(stack).state.nativeVariant,7);
 for(const nativeVariant of [-1,1.5,32768,'7'])assert.equal(normalizePublicFood({v:1,hotUntil:0,seasoning:[],nativeVariant}),undefined);
});
test('render providers preserve the explicitly published item variant',()=>{
 const stack={typeId:'minecraft:suspicious_stew',getComponent(){},clone(){return {...this}}};assert.equal(stationProjection(stack,{nativeVariant:7}).data,7);
 assert(registerStationProjection('test:custom',()=>({data:4})));assert(!registerStationProjection('test:custom',()=>({data:2})));
 assert.equal(stationProjection({...stack,typeId:'test:custom'},{}).data,4);assert.throws(()=>stationProjection(stack,{nativeVariant:32768}));
});
test('native equipment commands include and verify the declared aux data',()=>{
 const text=fs.readFileSync(scriptRoot+'station_contents_visual_runtime.js','utf8');const code=text.slice(text.indexOf('export function renderItemType('),text.indexOf('function pose('));const cmds=[];
 const ctx={stationProjection,readPublicFood:()=>({present:true,valid:true,state:{nativeVariant:7}})};vm.runInNewContext(code.replace('export ','' )+';this.run=renderItemType',ctx);
 const result=ctx.run({runCommand:c=>cmds.push(c)},{typeId:'minecraft:suspicious_stew',getComponent(){},clone(){return {...this}}});
 assert.equal(result.data,7);assert.equal(cmds[0],'replaceitem entity @s slot.weapon.mainhand 0 minecraft:suspicious_stew 1 7');assert(cmds[1].includes('data=7'));
});

test('minimum visual budget alternates departed cleanup and active refresh',()=>{
 const q=new VisualTargetQueue();q.add('departed',{dimensionId:'overworld',location:{x:100,y:0,z:0}});q.add('active',{dimensionId:'overworld',location:{x:0,y:0,z:0}});q.observe([{dimensionId:'overworld',x:100,y:0,z:0}]);q.observe([{dimensionId:'overworld',x:0,y:0,z:0}]);const visited=[...q.take(1),...q.take(1)];assert(visited.includes('departed'));assert(visited.includes('active'));q.observe([]);assert.deepEqual(q.take(1),['active']);assert.deepEqual(q.take(1),[]);
});
test('same actor wrappers share committed effects, caller edits and failed writes do not poison snapshots',()=>{
 const dp=new Map();let tick=1,reads=0,fail=false;
 const wrapper=()=>({id:'same-native-actor',getDynamicProperty(k){reads++;return dp.get(k)},setDynamicProperty(k,v){if(fail){dp.set(k,v);throw Error('after write')}if(v===undefined)dp.delete(k);else dp.set(k,v)}});
 const a=wrapper(),b=wrapper(),context={world:{getAbsoluteTime:()=>100},system:{get currentTick(){return tick}},activeEffects,effectPayload,milkEffects,FX_KEY};
 vm.runInNewContext(strip(fs.readFileSync(scriptRoot+'effect_state_runtime.js','utf8'))+';this.api={readEffects,writeEffects}',context);
 const api=context.api;api.readEffects(a);api.readEffects(b);assert.equal(reads,1);
 api.writeEffects(a,{vigor:{until:400,amp:0}});assert.equal(api.readEffects(b).vigor.until,400);
 const draft=api.readEffects(b);draft.vigor.until=600;assert.equal(api.readEffects(a).vigor.until,400);api.writeEffects(b,draft);assert.equal(api.readEffects(a).vigor.until,600);
 fail=true;assert.throws(()=>api.writeEffects(a,{warmth:{until:500,amp:0}}));assert.equal(api.readEffects(b).warmth.until,500);assert.equal(api.readEffects(b).vigor,undefined);tick++;assert.equal(api.readEffects(a).warmth.until,500);
});
