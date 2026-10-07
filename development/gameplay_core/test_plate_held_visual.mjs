/** Focused shared-channel projection checks; these do not certify native Molang rendering. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as plate from '../../projects/grilling/gameplay_core/behavior_pack/scripts/plate_held_visual_core.js';
import * as bottle from '../../projects/grilling/gameplay_core/behavior_pack/scripts/bottle_held_visual_core.js';
import * as registry from '../../projects/grilling/gameplay_core/behavior_pack/scripts/integration_registry_core.js';
import {secretVisualState as productionSecretVisualState} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/secret_visual_state.js';
import * as seasoning from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
import {RAW_TO_COOKED} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/data.js';
import {GRILL_MODEL_INDEX} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/grill_visual_data.js';
import {encodeSecretVisual} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/secret_visual_state_core.js';
const N='kaleidoscope_grilling:',PLATE=N+'skewer_plate',EMPTY=N+'empty_seasoning_bottle';
const ROOT=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
const plain=v=>JSON.parse(JSON.stringify(v));
const read=name=>fs.readFileSync(new URL(name,ROOT),'utf8');

function fixture({productionSecret=false}={}){
 const callbacks={},properties=new Map(),writes=[],warnings=[],states=[],restored=[],stats={rawPlateReads:0,plateDecodes:0,restores:0,secretReads:0};
 let main,off,failure,readFailure,qaEnabled=false;
 const player={id:'plate-holder',selectedSlotIndex:0,hasTag:tag=>qaEnabled&&tag==='kg_plate_qa',getProperty:key=>properties.get(key),getComponent(id){
  if(id==='minecraft:inventory')return {container:{size:9,getItem:()=>main,setItem(){throw Error('Inventory mutation')}}};
  if(id==='minecraft:equippable')return {getEquipment:()=>off,setEquipment(){throw Error('Equipment mutation')}};
 },setProperty(key,value){
  writes.push([key,value]);const rejected=failure?.(key,value,writes.length);
  if(rejected==='before')throw Error('Property rejection before mutation');
  properties.set(key,value);states.push(new Map(properties));
  if(rejected==='after')throw Error('Property rejection after mutation');
 }};
 const world={afterEvents:Object.fromEntries(['playerInventoryItemChange','playerHotbarSelectedSlotChange','playerLeave'].map(name=>[name,{subscribe:f=>callbacks[name]=f}])),getAllPlayers:()=>[player]};
 const system={run:f=>f(),runInterval:f=>callbacks.interval=f};
 const context=vm.createContext({...plate,...bottle,...seasoning,heldVisualRegistryRevision:registry.heldVisualRegistryRevision,PLATE_ID:PLATE,PLATE_SKEWERS_KEY:N+'plate_skewers',SECRET_MODEL_VARIANTS_KEY:N+'model_variants',world,system,console:{warn:s=>warnings.push(s)},
  getMainHand:()=>main,getOffHand:()=>off,
  getItemProperty(stack,key){if(key===N+'plate_skewers')stats.rawPlateReads++;if(stack===readFailure)throw Error('Unreadable native item');return stack?.props?.[key]},
  a25PlateRows(stack){stats.plateDecodes++;if(stack===readFailure)throw Error('Unreadable native plate');return stack.rows},
  a25RestoreStack(row){stats.restores++;restored.push(row);return row?.unavailable?undefined:row},
  secretVisualState:(stack,reader)=>{stats.secretReads++;return productionSecret?productionSecretVisualState(stack,reader):stack.visual}
 });
 vm.runInContext(strip(read('bottle_held_visual_runtime.js')),context);
 const api=vm.runInContext('({syncBottleHeld,configurePlateHeldReader,isDefaultFailedHeldVisual,heldClientProbeFlag})',context);
 api.configurePlateHeldReader(stack=>JSON.parse(stack.props?.[N+'skewer_ingredients']??'[]'));
 const stack=(typeId,props={})=>Object.freeze({typeId,props:Object.freeze(props),amount:1,maxAmount:1,getDynamicProperty:key=>props[key],nameTag:'Keep native name',setDynamicProperty(){throw Error('Metadata mutation')},setLore(){throw Error('Lore mutation')}});
 const plateStack=rows=>Object.freeze({...stack(PLATE,{[N+'plate_skewers']:JSON.stringify(rows)}),rows:Object.freeze(rows)});
 const bottleStack=(ids,typeId=EMPTY)=>stack(typeId,{[seasoning.SEASONING_LIST_KEY]:JSON.stringify(ids)});
 return {api,player,properties,writes,warnings,states,restored,stats,stack,plateStack,bottleStack,callbacks,get main(){return main},set main(v){main=v},get off(){return off},set off(v){off=v},fail(f){failure=f},failRead(s){readFailure=s},setQa(value){qaEnabled=value},words(hand){return Array.from({length:8},(_,i)=>properties.get(N+'bottle_'+hand+'_'+i))}};
}

const raws=Object.keys(GRILL_MODEL_INDEX).sort();
test('all38 fixed raw/cooked rows and retained eating aliases have exact descriptors',()=>{
 for(const raw of raws){const i=GRILL_MODEL_INDEX[raw];
  assert.deepEqual(plate.plateHeldRowPlan({typeId:raw}),{descriptor:1+i*2,palette:0});
  const cooked=RAW_TO_COOKED[raw];
  assert.deepEqual(plate.plateHeldRowPlan({typeId:cooked}),{descriptor:2+i*2,palette:0});
  assert.deepEqual(plate.plateHeldRowPlan({typeId:cooked+'_native_plain'}),{descriptor:2+i*2,palette:0});
 }
 assert.deepEqual(plate.plateHeldRowPlan({typeId:'external:tagged_skewer'}),{descriptor:0,palette:0});
});
test('all81 secret shape/style descriptors preserve three independent palettes',()=>{
 const seen=new Set();
 for(const style of [0,4,6])for(let a=1;a<=3;a++)for(let b=1;b<=3;b++)for(let c=1;c<=3;c++){
  const values=[a,b,c].map((shape,i)=>encodeSecretVisual([0,101,213][i]||1,shape,style===6?4:style,style===6)-(i===0?1:0));
  const stack=Object.freeze({typeId:N+'secret_skewer_java_three_alt'});
  const row=plate.plateHeldRowPlan(stack,()=>values);seen.add(row.descriptor);
  assert.equal(row.descriptor,39+(a-1)*9+(b-1)*3+c-1+[0,4,6].indexOf(style)*27);
  assert.equal(row.palette,plate.packPlatePalette([0,101,213]));
 }
 assert.equal(seen.size,81);assert.equal(Math.min(...seen),39);assert.equal(Math.max(...seen),119);
});
test('radix214 uses the complete exact float32-safe domain and rejects invalid palette input',()=>{
 assert.equal(plate.PLATE_HELD_PALETTE_MAX,9800343);assert.ok(plate.PLATE_HELD_PALETTE_MAX<2**24);
 assert.equal(plate.packPlatePalette([213,213,213]),9800343);
 for(const bad of [[214,0,0],[-1,0,0],[0,1.1,0],[0,0],null])assert.throws(()=>plate.packPlatePalette(bad));
 // Emulate single-precision at every Molang arithmetic boundary. Exhaustive
 // domain coverage is numerical evidence only; root still owns native checks.
 const f=Math.fround;
 for(let word=0;word<=9800343;word++){
  const q214=Math.floor(f(f(word)/f(214))),q45796=Math.floor(f(f(word)/f(45796)));
  const p0=f(f(word)-f(f(q214)*f(214))),p1=f(f(q214)-f(f(q45796)*f(214))),p2=q45796;
  if(p0!==word%214||p1!==Math.floor(word/214)%214||p2!==Math.floor(word/45796))throw Error('Float32 palette decode failed at '+word);
 }
});
test('paired row words, count boundaries and owner sentinels decode without borrowed row data',()=>{
 for(let a=0;a<123;a++)for(let b=0;b<123;b++){
  const word=a+123*b;assert.equal(Math.floor(Math.fround(word/123)),b);assert.equal(word-123*b,a);
 }
 for(let count=0;count<=5;count++)for(let d=0;d<123;d++){
  const marker=10+d+123*count,decoded=plate.decodePlateHeldVisual([0,0,0,0,0,0,0,marker]);
  assert.equal(decoded.count,count);assert.equal(decoded.rows[4].descriptor,d);
 }
 for(const marker of [-1,0,9,748,9800343])assert.equal(plate.decodePlateHeldVisual([0,0,0,0,0,0,0,marker]),undefined);
 assert.equal(plate.decodePlateHeldVisual([0,0,0,0,0,15129,0,10]),undefined);
});
test('count0–5 use actual row order without changing source metadata',()=>{
 for(let count=0;count<=5;count++){
  const stacks=Object.freeze(raws.slice(0,count).map(typeId=>Object.freeze({typeId})));
  const packed=plate.plateHeldVisualPlan(stacks),decoded=plate.decodePlateHeldVisual(packed);
  assert.equal(decoded.count,count);assert.deepEqual(decoded.rows.map(r=>r.descriptor),Array.from({length:5},(_,i)=>i<count?1+i*2:0));
  assert.equal(stacks.length,count);
 }
 assert.throws(()=>plate.plateHeldVisualPlan(Array(6).fill({typeId:raws[0]})));
});
test('authored special defaults render; retained non-default failure metadata stays explicitly unsupported',()=>{
 const f=fixture();
 for(const [id,d] of [['ordinary_skewer',120],['mysterious_skewer',121],['dark_grilling',122]]){
  const stack=f.stack(N+id);assert.equal(plate.plateHeldRowPlan(stack,undefined,f.api.isDefaultFailedHeldVisual).descriptor,d);
 }
 for(const id of ['mysterious_skewer','dark_grilling'])for(const raw of ['[4,5,6]','broken','{}','[1]',true]){
  const props=Object.freeze({[N+'model_variants']:raw}),stack=f.stack(N+id,props);
  assert.equal(plate.plateHeldRowPlan(stack,undefined,f.api.isDefaultFailedHeldVisual).descriptor,0);assert.strictEqual(stack.props,props);
 }
 for(const raw of [undefined,'[]'])assert.equal(f.api.isDefaultFailedHeldVisual(f.stack(N+'dark_grilling',{[N+'model_variants']:raw})),true);
});
test('plate+bottle, bottle+plate and two distinct plates publish independent hands',()=>{
 const f=fixture(),first=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[1]])]),second=f.plateStack([f.stack(N+'ordinary_skewer')]),b=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[6]]);
 for(const [main,off] of [[first,b],[b,first],[first,second],[second,first]]){
  f.main=main;f.off=off;f.api.syncBottleHeld(f.player);
  for(const hand of ['main','off']){
   const native=f[hand];if(native.typeId===PLATE)assert.equal(plate.decodePlateHeldVisual(f.words(hand)).count,native.rows.length);
   else assert.deepEqual(f.words(hand),[7,0,0,0,0,0,0,0]);
   assert.strictEqual(f[hand],native);assert.equal(native.nameTag,'Keep native name');
  }
 }
});
test('both owners invalidate before payload writes and each valid marker is released last',()=>{
 const f=fixture();f.main=f.plateStack([f.stack(raws[0])]);f.off=f.bottleStack(bottle.BOTTLE_HELD_INGREDIENT_IDS);f.api.syncBottleHeld(f.player);
 assert.equal(f.writes.length,18);
 assert.deepEqual(f.writes.slice(0,2),[[N+'bottle_main_7',748],[N+'bottle_off_7',748]]);
 assert.ok(f.writes.slice(2,16).every(([key])=>!key.endsWith('_7')));
 assert.deepEqual(f.writes.slice(16),[[N+'bottle_main_7',133],[N+'bottle_off_7',8]]);
 for(const state of f.states.slice(1,16))for(const hand of ['main','off'])assert.equal(state.get(N+'bottle_'+hand+'_7'),748);
 f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,18);
});
for(const mode of ['before','after'])for(let position=1;position<=18;position++)test(`partial shared-word write ${position} ${mode} mutation recovers even when hands revert`,()=>{
 const f=fixture(),originalMain=f.plateStack([f.stack(raws[0])]),originalOff=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]]);
 f.main=originalMain;f.off=originalOff;f.api.syncBottleHeld(f.player);const expectedMain=f.words('main'),expectedOff=f.words('off');
 f.main=f.bottleStack(bottle.BOTTLE_HELD_INGREDIENT_IDS);f.off=f.plateStack([f.stack(raws[1]),f.stack(raws[2])]);
 const first=f.writes.length;f.fail((_key,_value,n)=>n===first+position?mode:false);f.callbacks.interval();assert.equal(f.warnings.length,1);
 f.main=originalMain;f.off=originalOff;const attempts=f.writes.length;f.callbacks.interval();assert.equal(f.writes.length,attempts+18);
 assert.deepEqual(f.words('main'),expectedMain);assert.deepEqual(f.words('off'),expectedOff);
 f.callbacks.interval();assert.equal(f.writes.length,attempts+18);
});
test('unreadable plate/restore input does not publish partial plans; readable retry succeeds',()=>{
 const f=fixture(),a=f.plateStack([f.stack(raws[0])]),b=f.plateStack([f.stack(raws[1])]);f.main=a;f.off=b;f.failRead(b);f.callbacks.interval();assert.equal(f.writes.length,2);
 assert.equal(plate.decodePlateHeldVisual(f.words('main')),undefined);assert.equal(plate.decodePlateHeldVisual(f.words('off')),undefined);
 f.failRead(undefined);f.callbacks.interval();assert.equal(f.writes.length,20);
 f.main=f.plateStack([Object.freeze({id:raws[2],unavailable:true})]);f.callbacks.interval();assert.equal(f.writes.length,22);
 assert.equal(plate.decodePlateHeldVisual(f.words('main')),undefined);assert.equal(plate.decodePlateHeldVisual(f.words('off')),undefined);
 f.main=a;f.callbacks.interval();assert.equal(f.writes.length,40,'Input failure invalidates the output signature so reverted valid hands recover');
});
test('plate to other item clears all words and player leave discards projection cache',()=>{
 const f=fixture();f.main=f.plateStack([f.stack(raws[0])]);f.off=f.plateStack([]);f.api.syncBottleHeld(f.player);
 f.main=f.stack('minecraft:stone');f.off=undefined;f.api.syncBottleHeld(f.player);assert.deepEqual(f.words('main'),Array(8).fill(0));assert.deepEqual(f.words('off'),Array(8).fill(0));
 f.callbacks.playerLeave({playerId:f.player.id});f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,54);
});

test('unchanged held plate copies poll one raw snapshot without repeated decode/restore or property writes',()=>{
 const f=fixture(),rows=raws.slice(0,5).map(id=>f.stack(id));f.main=f.plateStack(rows);f.api.syncBottleHeld(f.player);
 assert.deepEqual(f.stats,{rawPlateReads:1,plateDecodes:1,restores:5,secretReads:0});assert.equal(f.writes.length,18);
 for(let i=0;i<100;i++){f.main=f.plateStack(rows);f.callbacks.interval();}
 assert.deepEqual(f.stats,{rawPlateReads:101,plateDecodes:1,restores:5,secretReads:0});assert.equal(f.writes.length,18);
 const changed=[f.stack(RAW_TO_COOKED[raws[0]]),...rows.slice(1)];f.main=f.plateStack(changed);f.callbacks.interval();
 assert.equal(f.stats.plateDecodes,2);assert.equal(f.stats.restores,10);assert.equal(f.writes.length,36);
 f.main=f.plateStack(changed.slice(1));f.callbacks.interval();assert.equal(f.stats.plateDecodes,3);assert.equal(f.stats.restores,14);assert.equal(f.writes.length,54);
 // An authoritative inventory callback discards input caches; an identical
 // result still reuses the successful output signature rather than rewriting.
 f.callbacks.playerInventoryItemChange({player:f.player});assert.equal(f.stats.plateDecodes,4);assert.equal(f.stats.restores,18);assert.equal(f.writes.length,54);
 f.main=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[1]]);f.callbacks.interval();
 f.main=f.plateStack(changed.slice(1));f.callbacks.interval();assert.equal(f.stats.plateDecodes,5);assert.equal(f.stats.restores,22);
});
test('property-write retries reuse a valid derived input plan while reader changes invalidate it',()=>{
 const f=fixture(),secret=Object.freeze({...f.stack(N+'secret_skewer'),visual:[1,2,3]});f.main=f.plateStack([secret]);
 f.fail((_key,_value,n)=>n===3?'after':false);f.callbacks.interval();assert.equal(f.stats.plateDecodes,1);assert.equal(f.stats.restores,1);assert.equal(f.stats.secretReads,1);
 f.callbacks.interval();assert.equal(f.stats.plateDecodes,1);assert.equal(f.stats.restores,1);assert.equal(f.stats.secretReads,1);assert.equal(plate.decodePlateHeldVisual(f.words('main')).count,1);
 f.api.configurePlateHeldReader(()=>[]);f.callbacks.interval();assert.equal(f.stats.plateDecodes,2);assert.equal(f.stats.restores,2);assert.equal(f.stats.secretReads,2);
});

test('production secret state refreshes unchanged plate snapshots after held registration/reset/restore, but replay and unrelated registry edits stay cached',()=>{
 registry.resetIntegrationRegistry();
 const f=fixture({productionSecret:true}),rows=[{id:'external:held_food'},{id:'minecraft:apple'},{id:'minecraft:carrot'}];
 const secret=f.stack(N+'secret_skewer',{[N+'skewer_ingredients']:JSON.stringify(rows),[N+'model_variants']:'[4,5,6]'});
 const original=f.plateStack([secret]);f.main=original;f.api.syncBottleHeld(f.player);
 assert.equal(f.words('main')[0],8280516);assert.equal(f.stats.secretReads,1);
 const initialRevision=registry.heldVisualRegistryRevision();
 registry.registerProducer({producerId:'external:producer',items:['minecraft:apple'],kinds:['cuisine']});
 registry.registerProjectionDescriptor({itemId:'external:held_food',provider:'external:display'});
 assert.equal(registry.heldVisualRegistryRevision(),initialRevision);f.callbacks.interval();assert.equal(f.stats.secretReads,1);assert.equal(f.writes.length,18);
 const registration={itemId:'external:held_food',referenceItemId:'minecraft:apple'};
 assert.equal(registry.registerHeldVisual(registration).replayed,false);assert.equal(registry.heldVisualRegistryRevision(),initialRevision+1);
 f.callbacks.interval();assert.equal(f.words('main')[0],8280690);assert.equal(f.stats.secretReads,2);assert.equal(f.writes.length,36);assert.strictEqual(f.main,original);
 const saved=registry.integrationRegistrySnapshot(),activeRevision=registry.heldVisualRegistryRevision();
 assert.equal(registry.registerHeldVisual(registration).replayed,true);assert.equal(registry.heldVisualRegistryRevision(),activeRevision);
 assert.throws(()=>registry.registerHeldVisual({...registration,referenceItemId:'minecraft:bread'}),/conflict/);assert.equal(registry.heldVisualRegistryRevision(),activeRevision);
 for(let i=0;i<20;i++)f.callbacks.interval();assert.equal(f.stats.secretReads,2);assert.equal(f.writes.length,36);
 registry.resetIntegrationRegistry();f.callbacks.interval();assert.equal(f.words('main')[0],8280516);assert.equal(f.stats.secretReads,3);assert.equal(f.writes.length,54);
 const emptyRevision=registry.heldVisualRegistryRevision();registry.resetIntegrationRegistry();assert.equal(registry.heldVisualRegistryRevision(),emptyRevision);f.callbacks.interval();assert.equal(f.stats.secretReads,3);
 registry.restoreIntegrationRegistry(saved);f.callbacks.interval();assert.equal(f.words('main')[0],8280690);assert.equal(f.stats.secretReads,4);assert.equal(f.writes.length,72);
 // A synchronous restore with the same held mapping, including unrelated
 // producer/projection rollback, retains both input and output caches.
 const restoredRevision=registry.heldVisualRegistryRevision();
 registry.restoreIntegrationRegistry(saved);assert.equal(registry.heldVisualRegistryRevision(),restoredRevision);f.callbacks.interval();assert.equal(f.stats.secretReads,4);assert.equal(f.writes.length,72);
 registry.restoreIntegrationRegistry({...saved,producers:[],projections:[]});assert.equal(registry.heldVisualRegistryRevision(),restoredRevision);f.callbacks.interval();assert.equal(f.stats.secretReads,4);
 assert.throws(()=>registry.restoreIntegrationRegistry({...saved,held:[registration,{itemId:'external:bad',referenceItemId:'external:unknown_texture'}]}),/resource release/);
 f.callbacks.interval();assert.equal(f.words('main')[0],8280516);assert.equal(f.stats.secretReads,5);assert.equal(f.writes.length,90);
 registry.restoreIntegrationRegistry({...saved,held:[{...registration,referenceItemId:'minecraft:bread'}]});f.callbacks.interval();assert.equal(f.words('main')[0],8280516+179);assert.equal(f.stats.secretReads,6);
 assert.deepEqual(secret.props,{[N+'skewer_ingredients']:JSON.stringify(rows),[N+'model_variants']:'[4,5,6]'});assert.strictEqual(f.main,original);
 registry.resetIntegrationRegistry();
});

const plateDescription=JSON.parse(fs.readFileSync(new URL('../../projects/grilling/gameplay_core/resource_pack/attachables/skewer_plate.attachable.json',import.meta.url),'utf8'))['minecraft:attachable']['description'];
const plateControllers=JSON.parse(fs.readFileSync(new URL('../../projects/grilling/gameplay_core/resource_pack/render_controllers/plate_held.render_controllers.json',import.meta.url),'utf8')).render_controllers;
function renderedPlate(f,hand){
 const v={},c={item_slot:hand+'_hand'},math={floor:Math.floor,clamp:(n,a,b)=>Math.max(a,Math.min(b,n))};
 const owner={has_property:key=>f.properties.has(key),property:key=>f.properties.get(key),is_item_name_any:(slot,...ids)=>ids.includes(f[slot==='slot.weapon.mainhand'?'main':'off']?.typeId)};
 for(const row of plateDescription.scripts.pre_animation)new Function('owner','c','v','math',row.replaceAll('c.owning_entity->q.','owner.'))(owner,c,v,math);
 const visible=Object.values(plateControllers).filter(rc=>Boolean(new Function('v','math','return '+Object.values(rc.part_visibility.at(-1))[0])(v,math))).length;
 return {owner:Boolean(v.kg_plate_owner_occupied),visible,count:v.kg_plate_count};
}
for(const hand of ['main','off'])for(const failureType of ['read','restore'])test(`${hand} prior-success plate A to unreadable plate B suppresses real generated passes and reverting A restores both projections (${failureType})`,()=>{
 const f=fixture(),opposite=hand==='main'?'off':'main',a=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[0]])]);
 const b=f.plateStack([failureType==='restore'?Object.freeze({typeId:N+'ordinary_skewer',unavailable:true}):f.stack(N+'ordinary_skewer')]);
 f[hand]=a;f[opposite]=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]]);f.api.syncBottleHeld(f.player);
 assert.equal(f.words(hand)[7],256);assert.deepEqual(renderedPlate(f,hand),{owner:true,visible:3,count:2});
 f[hand]=b;if(failureType==='read')f.failRead(b);f.callbacks.interval();assert.equal(f.warnings.length,1);
 assert.equal(f.words(hand)[7],748);assert.equal(f.words(opposite)[7],748);assert.equal(renderedPlate(f,hand).owner,false);assert.equal(renderedPlate(f,hand).visible,0);assert.strictEqual(f[hand],b);
 f[hand]=a;f.callbacks.interval();assert.equal(f.words(hand)[7],256);assert.deepEqual(renderedPlate(f,hand),{owner:true,visible:3,count:2});assert.deepEqual(f.words(opposite),[1,0,0,0,0,0,0,0]);assert.equal(f.writes.length,38);
 f.callbacks.interval();assert.equal(f.writes.length,38);
});
for(const hand of ['main','off'])for(const mode of ['before','after'])for(const blocked of ['affected_marker','opposite_marker','both_markers','marker_and_first_pair'])test(`${hand} unreadable input handles ${blocked} setter rejection ${mode} mutation independently and retries after revert`,()=>{
 const f=fixture(),opposite=hand==='main'?'off':'main',a=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[0]])]),b=f.plateStack([f.stack(N+'ordinary_skewer')]);
 f[hand]=a;f[opposite]=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[1]]);f.api.syncBottleHeld(f.player);
 f[hand]=b;f.failRead(b);
 const keys=new Set(blocked==='affected_marker'?[N+'bottle_'+hand+'_7']:blocked==='opposite_marker'?[N+'bottle_'+opposite+'_7']:blocked==='both_markers'?[N+'bottle_main_7',N+'bottle_off_7']:[N+'bottle_'+hand+'_7',N+'bottle_'+hand+'_5']);
 f.fail(key=>keys.has(key)?mode:false);f.callbacks.interval();assert.equal(f.warnings.length,1);assert.match(f.warnings[0],/invalidation rejected/);
 assert.equal(renderedPlate(f,hand).owner,false);assert.equal(renderedPlate(f,hand).visible,0);
 const attempted=f.writes.slice(18).map(([key])=>key);assert.ok(attempted.includes(N+'bottle_main_7'));assert.ok(attempted.includes(N+'bottle_off_7'),'A rejection must not skip the opposite invalidation attempt');
 f.fail(()=>false);f[hand]=a;const writes=f.writes.length;f.callbacks.interval();assert.equal(f.writes.length,writes+18);assert.deepEqual(renderedPlate(f,hand),{owner:true,visible:3,count:2});assert.deepEqual(f.words(opposite),[2,0,0,0,0,0,0,0]);
});
test('complete setter refusal reports the inability to invalidate, clears the output cache, and recovers when setters become writable',()=>{
 const f=fixture(),a=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[0]])]),b=f.plateStack([f.stack(N+'ordinary_skewer')]);f.main=a;f.off=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]]);f.api.syncBottleHeld(f.player);
 f.main=b;f.failRead(b);f.fail(()=> 'before');f.callbacks.interval();assert.equal(f.warnings.length,1);assert.match(f.warnings[0],/main owner/);assert.match(f.warnings[0],/off owner/);assert.match(f.warnings[0],/main pair5/);assert.match(f.warnings[0],/main pair6/);
 // No accepted setter can mean no client-state change. This external failure
 // is explicitly reported, rather than falsely claiming owner invalidation.
 assert.equal(f.writes.length,24);assert.equal(renderedPlate(f,'main').owner,true);
 f.fail(()=>false);f.main=a;f.callbacks.interval();assert.equal(f.writes.length,42);assert.deepEqual(renderedPlate(f,'main'),{owner:true,visible:3,count:2});
});

const bottleDescriptions=Object.fromEntries(['empty_seasoning_bottle','pending_seasoning'].map(name=>[N+name,JSON.parse(fs.readFileSync(new URL('../../projects/grilling/gameplay_core/resource_pack/attachables/'+name+'.attachable.json',import.meta.url),'utf8'))['minecraft:attachable']['description']]));
const dynamicBottleController=JSON.parse(fs.readFileSync(new URL('../../projects/grilling/gameplay_core/resource_pack/render_controllers/bottle_held_contents.render_controllers.json',import.meta.url),'utf8')).render_controllers['controller.render.kg_bottle_held.dynamic'];
function renderedBottle(f,hand){
 const d=bottleDescriptions[f[hand]?.typeId];assert.ok(d,'Fixture needs a known dynamic bottle item');
 const v={},c={item_slot:hand+'_hand'},math={floor:Math.floor,clamp:(n,a,b)=>Math.max(a,Math.min(b,n))};
 const owner={has_property:key=>f.properties.has(key),property:key=>f.properties.get(key),is_item_name_any:(slot,...ids)=>ids.includes(f[slot==='slot.weapon.mainhand'?'main':'off']?.typeId)};
 for(const row of d.scripts.pre_animation.filter(row=>row.startsWith('v.kg_bottle_')))new Function('owner','c','v','math',row.replaceAll('c.owning_entity->q.','owner.'))(owner,c,v,math);
 const contents=dynamicBottleController.part_visibility.flatMap(row=>Object.entries(row)).filter(([bone,expression])=>bone.startsWith('pending_')&&Boolean(new Function('v','math','return '+expression)(v,math))).length;
 return {owner:Boolean(v.kg_bottle_owner_occupied),contents};
}
for(const plateHand of ['main','off'])for(const recovery of ['changed','revert'])test(`${plateHand} changed plate plus opposite bottle read fault invalidates both real predicates and supports ${recovery} recovery`,()=>{
 const f=fixture(),bottleHand=plateHand==='main'?'off':'main',a=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[0]])]),b=f.plateStack([f.stack(N+'ordinary_skewer')]);
 const originalBottle=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]],N+'pending_seasoning'),unreadableBottle=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[7]],N+'pending_seasoning');
 f[plateHand]=a;f[bottleHand]=originalBottle;f.api.syncBottleHeld(f.player);assert.equal(f.words(plateHand)[7],256);assert.equal(renderedPlate(f,plateHand).visible,3);
 f[plateHand]=b;f[bottleHand]=unreadableBottle;f.failRead(unreadableBottle);f.callbacks.interval();assert.equal(f.writes.length,20);assert.equal(f.warnings.length,1);
 assert.equal(renderedPlate(f,plateHand).owner,false);assert.equal(renderedPlate(f,plateHand).visible,0);assert.deepEqual(renderedBottle(f,bottleHand),{owner:false,contents:0});assert.strictEqual(f[plateHand],b);assert.strictEqual(f[bottleHand],unreadableBottle);
 if(recovery==='revert'){f[plateHand]=a;f[bottleHand]=originalBottle;}else f.failRead(undefined);
 f.callbacks.interval();assert.equal(f.writes.length,38);assert.equal(renderedPlate(f,plateHand).visible,recovery==='revert'?3:2);assert.equal(f.words(plateHand)[7],recovery==='revert'?256:133);assert.deepEqual(renderedBottle(f,bottleHand),{owner:true,contents:2});
 f.callbacks.interval();assert.equal(f.writes.length,38);
});
for(const badHand of ['main','off'])for(const recovery of ['changed','revert'])test(`standalone two-bottle ${badHand} input fault closes both passes and ${recovery} recovery restores complete words`,()=>{
 const f=fixture(),main=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]]),off=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[1],bottle.BOTTLE_HELD_INGREDIENT_IDS[2]],N+'pending_seasoning');
 f.main=main;f.off=off;f.api.syncBottleHeld(f.player);
 const changedMain=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[7]]),changedOff=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[6]],N+'pending_seasoning');f.main=changedMain;f.off=changedOff;f.failRead(f[badHand]);f.callbacks.interval();assert.equal(f.writes.length,20);
 for(const hand of ['main','off'])assert.deepEqual(renderedBottle(f,hand),{owner:false,contents:0});
 if(recovery==='revert'){f.main=main;f.off=off;}else f.failRead(undefined);
 f.callbacks.interval();assert.equal(f.writes.length,38);assert.deepEqual(f.words('main'),[recovery==='revert'?1:8,0,0,0,0,0,0,0]);assert.deepEqual(f.words('off'),recovery==='revert'?[2,3,0,0,0,0,0,0]:[7,0,0,0,0,0,0,0]);
 for(const hand of ['main','off'])assert.equal(renderedBottle(f,hand).owner,true);
});
for(const plateHand of ['main','off'])for(const mode of ['before','after'])for(const blocked of ['plate_marker','bottle_marker','both_markers_and_pair5'])test(`${plateHand} mixed bottle input fault handles ${blocked} setter failures ${mode} mutation through shared pair guards`,()=>{
 const f=fixture(),bottleHand=plateHand==='main'?'off':'main',a=f.plateStack([f.stack(raws[0]),f.stack(RAW_TO_COOKED[raws[0]])]),b=f.plateStack([f.stack(N+'ordinary_skewer')]);
 const originalBottle=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[0]]),bad=f.bottleStack([bottle.BOTTLE_HELD_INGREDIENT_IDS[7]]);f[plateHand]=a;f[bottleHand]=originalBottle;f.api.syncBottleHeld(f.player);
 f[plateHand]=b;f[bottleHand]=bad;f.failRead(bad);const keys=new Set(blocked==='plate_marker'?[N+'bottle_'+plateHand+'_7']:blocked==='bottle_marker'?[N+'bottle_'+bottleHand+'_7']:[N+'bottle_main_7',N+'bottle_off_7',N+'bottle_main_5',N+'bottle_off_5']);f.fail(key=>keys.has(key)?mode:false);f.callbacks.interval();assert.equal(f.warnings.length,1);assert.match(f.warnings[0],/invalidation rejected/);
 assert.equal(renderedPlate(f,plateHand).owner,false);assert.equal(renderedPlate(f,plateHand).visible,0);assert.deepEqual(renderedBottle(f,bottleHand),{owner:false,contents:0});
 f.fail(()=>false);f[plateHand]=a;f[bottleHand]=originalBottle;const writes=f.writes.length;f.callbacks.interval();assert.equal(f.writes.length,writes+18);assert.equal(renderedPlate(f,plateHand).visible,3);assert.deepEqual(renderedBottle(f,bottleHand),{owner:true,contents:2});
});

test('client QA flag uses only dormant word4 for the exact opt-in one-row fixture and clears on opt-out without item or cached-plan mutation',()=>{
 const f=fixture({productionSecret:true}),secret=f.stack(N+'secret_skewer_java_three_alt',{[N+'skewer_ingredients']:JSON.stringify([{id:'minecraft:mushroom_stew'},{id:'minecraft:golden_apple'},{id:'minecraft:carrot'}]),[N+'model_variants']:'[9,4,7]'}),native=f.plateStack([secret]);f.main=native;
 f.api.syncBottleHeld(f.player);assert.deepEqual(f.words('main'),[8285209,0,0,0,0,57,0,133]);assert.equal(f.stats.restores,1);
 f.setQa(true);f.api.syncBottleHeld(f.player);assert.deepEqual(f.words('main'),[8285209,0,0,0,1,57,0,133]);assert.equal(f.stats.restores,1);assert.strictEqual(f.main,native);assert.equal(f.writes.length,36);
 f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,36);
 f.setQa(false);f.api.syncBottleHeld(f.player);assert.deepEqual(f.words('main'),[8285209,0,0,0,0,57,0,133]);assert.equal(f.stats.restores,1);assert.equal(f.writes.length,54);
 f.setQa(true);f.api.syncBottleHeld(f.player);assert.equal(f.words('main')[4],1,'Opt-out must not alter the cached production plan');assert.strictEqual(f.main,native);assert.equal(f.stats.restores,1);
});
test('client QA flag rejects other items, shapes, counts, existing row4 data, disabled tags and tag-query failures',()=>{
 const f=fixture(),target=Object.freeze([8285209,0,0,0,0,57,0,133]),plateStack=f.plateStack([]);assert.equal(f.api.heldClientProbeFlag(f.player,plateStack,target),false);f.setQa(true);assert.equal(f.api.heldClientProbeFlag(f.player,plateStack,target),true);
 for(const [index,value] of [[0,8285208],[1,1],[4,1],[5,39],[6,1],[7,625]]){const changed=[...target];changed[index]=value;assert.equal(f.api.heldClientProbeFlag(f.player,plateStack,changed),false);}
 assert.equal(f.api.heldClientProbeFlag(f.player,f.stack(N+'secret_skewer'),target),false);assert.equal(f.api.heldClientProbeFlag({hasTag(){throw Error('unavailable tag')}},plateStack,target),false);assert.deepEqual(target,[8285209,0,0,0,0,57,0,133]);
});
