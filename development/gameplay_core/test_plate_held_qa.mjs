/** Default-off source QA; server property readings are not client Molang evidence. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const N='kaleidoscope_grilling:',PLATE=N+'skewer_plate',VARIANTS=N+'model_variants';
const code=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/bottle_held_visual_runtime.js',import.meta.url),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
function fixture(){
 let enabled=false,main,off,readFailure=false,propertyFailure=false;
 const stats={hands:0,items:0,properties:0,writes:0},logs=[],properties=new Map(),events={},system={currentTick:0,run(){},runInterval(){}};
 const player={id:'private-player-identifier',name:'private-player-name',hasTag:tag=>enabled&&tag==='kg_plate_qa',getProperty(key){stats.properties++;if(propertyFailure)throw Error('read');return properties.get(key)},setProperty(){stats.writes++;throw Error('QA cannot write properties')}};
 const world={getAllPlayers:()=>[player],afterEvents:Object.fromEntries(['playerInventoryItemChange','playerHotbarSelectedSlotChange','playerLeave'].map(name=>[name,{subscribe:callback=>events[name]=callback}]))};
 const context=vm.createContext({PLATE_ID:PLATE,PLATE_SKEWERS_KEY:N+'plate_skewers',SECRET_MODEL_VARIANTS_KEY:VARIANTS,world,system,
  getMainHand(){stats.hands++;return main},getOffHand(){stats.hands++;return off},getItemProperty(stack,key){stats.items++;if(readFailure)throw Error('unreadable');return stack.props[key]},console:{warn:line=>logs.push(line)}});
 vm.runInContext(code,context);const trace=vm.runInContext('traceHeldProjection',context);
 const stack=rows=>Object.freeze({typeId:PLATE,props:Object.freeze({[N+'plate_skewers']:JSON.stringify(rows)}),setLore(){throw Error('QA lore mutation')},setDynamicProperty(){throw Error('QA metadata mutation')}});
 const words=(mainWords,offWords=Array(8).fill(0))=>Object.fromEntries(['main','off'].flatMap((hand,h)=>[...h?offWords:mainWords].map((value,i)=>[N+'bottle_'+hand+'_'+i,value])));
 return {trace,player,stats,logs,properties,events,system,stack,words,get enabled(){return enabled},set enabled(v){enabled=v},get main(){return main},set main(v){main=v},get off(){return off},set off(v){off=v},failRead(v){readFailure=v},failProperty(v){propertyFailure=v},records(){return logs.map(line=>JSON.parse(line.slice('[Grilling held QA] '.length)))}};
}
const row={id:N+'secret_skewer_java_three_alt',native:{id:N+'secret_skewer_java_three_alt',props:{[VARIANTS]:'[9,4,7]',[N+'creator']:'private creator data'},name:'private item name',rawLore:['private item lore']}};
test('held QA is disabled by default and does not read items/properties or write anything',()=>{
 const f=fixture();f.main=f.stack([row]);for(let i=0;i<100;i++){f.system.currentTick+=20;f.trace(f.player,f.words(Array(8).fill(0)));}
 assert.deepEqual(f.stats,{hands:0,items:0,properties:0,writes:0});assert.equal(f.logs.length,0);
});
test('enabled QA reports bounded public row/variants and projected versus server-live words without private fields or mutations',()=>{
 const f=fixture(),expected=[8285209,0,0,0,0,57,0,133],projected=f.words(expected);f.enabled=true;f.main=f.stack([row]);for(const [k,v]of Object.entries(projected))f.properties.set(k,v);
 f.trace(f.player,projected);const record=f.records()[0];assert.equal(record.phase,'ready');assert.deepEqual(record.main.rows,[{id:row.id,modelVariants:[9,4,7]}]);assert.deepEqual(record.main.projected,expected);assert.deepEqual(record.main.serverLive,expected);assert.equal(record.off.itemId,null);assert.equal(f.stats.writes,0);
 assert.doesNotMatch(f.logs[0],/private|rawLore|creator|nameTag/);assert.strictEqual(f.main.props[N+'plate_skewers'],JSON.stringify([row]));
});
test('QA rate gate, changed-only emission and activation cap are bounded, with reset after opt-out',()=>{
 const f=fixture();f.enabled=true;f.main=f.stack([row]);let projected=f.words(Array(8).fill(0));f.trace(f.player,projected);f.trace(f.player,f.words(Array(8).fill(1)));assert.equal(f.logs.length,1);
 f.system.currentTick=20;f.trace(f.player,projected);assert.equal(f.logs.length,1,'Unchanged record must not repeat');
 for(let i=1;i<=40;i++){f.system.currentTick+=20;projected=f.words(Array(8).fill(i));f.trace(f.player,projected);}assert.equal(f.logs.length,24);
 const reads=f.stats.properties;f.system.currentTick+=20;f.trace(f.player,f.words(Array(8).fill(99)));assert.equal(f.stats.properties,reads,'Cap stops further property reads');
 f.enabled=false;f.trace(f.player,projected);f.enabled=true;f.trace(f.player,projected);assert.equal(f.logs.length,25);
});
test('QA sanitizes invalid variant values and handles unreadable rows/properties without changing presentation',()=>{
 const f=fixture();f.enabled=true;f.main=f.stack([{id:'invalid private item id',props:{[VARIANTS]:'private secret-like text'}}]);f.trace(f.player,undefined,'input_failed');let r=f.records()[0];assert.equal(r.phase,'input_failed');assert.deepEqual(r.main.rows,[{id:'invalid',modelVariants:'invalid'}]);assert.deepEqual(r.main.projected,Array(8).fill(null));assert.doesNotMatch(f.logs[0],/private/);
 f.system.currentTick=20;f.failRead(true);f.failProperty(true);assert.doesNotThrow(()=>f.trace(f.player,undefined,'input_failed'));r=f.records()[1];assert.equal(r.main.rows,'unreadable');assert.deepEqual(r.main.serverLive,Array(8).fill('unreadable'));assert.equal(f.stats.writes,0);
 f.events.playerLeave({playerId:f.player.id});f.failRead(false);f.failProperty(false);f.trace(f.player,undefined,'input_failed');assert.equal(f.logs.length,3,'Leave clears the diagnostic activation cache');
});
test('QA publication-failure record distinguishes expected words from partially invalidated server state',()=>{
 const f=fixture();f.enabled=true;f.main=f.stack([row]);const expected=[8285209,0,0,0,0,57,0,133],projected=f.words(expected);for(const [k,v] of Object.entries(projected))f.properties.set(k,v);f.properties.set(N+'bottle_main_7',748);f.properties.set(N+'bottle_main_0',0);
 f.trace(f.player,projected,'publish_failed');const r=f.records()[0];assert.equal(r.phase,'publish_failed');assert.deepEqual(r.main.projected,expected);assert.deepEqual(r.main.serverLive,[0,0,0,0,0,57,0,748]);assert.equal(f.stats.writes,0);
});
