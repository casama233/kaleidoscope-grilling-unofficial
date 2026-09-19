/** Execute the UNMODIFIED Bedrock adapter in a mock event host. Not an engine test. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
let count=0;const check=(name,fn)=>{fn();count++;console.log('PASS',name);};
const events=Object.fromEntries(['entitySpawn','playerInteractWithEntity','playerSpawn'].map(k=>[k,{listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e)}}]));
const intervals=[],warnings=[];
const dimension={id:'minecraft:overworld',entities:[],getEntities:()=>dimension.entities,playSound:(...x)=>{},spawnParticle:(...x)=>{}};
const player={id:'player1',isSneaking:false,dimension,location:{x:0,y:0,z:0},sounds:[],stops:[],playSound(id,opts){this.sounds.push({id,opts,tick:system.currentTick})},runCommand(s){assert.match(s,/^stopsound @s kg_imm\.[a-z0-9_]+$/);this.stops.push(s)},onScreenDisplay:{setActionBar(s){}}};
const world={afterEvents:events,getAllPlayers:()=>[player],getDimension:()=>dimension};
const system={currentTick:0,run(f){f()},runInterval(f,interval){intervals.push({f,interval})}};
function entity(id,x=0){const data=new Map(),props=new Map();return {id,typeId:'kg_imm:rehearsal',isValid:true,location:{x,y:0,z:0},dimension,props,getDynamicProperty:k=>data.get(k),setDynamicProperty:(k,v)=>data.set(k,v),setProperty:(k,v)=>props.set(k,v)}}
const ctx=vm.createContext({console:{warn:(...x)=>warnings.push(x)},Math,JSON,Map,Set,Object,Array,Number,String,Error,Boolean});
const module=new vm.SourceTextModule(fs.readFileSync(new URL('./main.js',import.meta.url),'utf8'),{context:ctx});
const flow=new vm.SourceTextModule(fs.readFileSync(new URL('./flow.js',import.meta.url),'utf8'),{context:ctx});
const server=new vm.SyntheticModule(['world','system'],function(){this.setExport('world',world);this.setExport('system',system)},{context:ctx});
const audio=new vm.SyntheticModule(['AUDIO'],function(){this.setExport('AUDIO',{grill_loop:{duration:2}})},{context:ctx});
await module.link(name=>name==='@minecraft/server'?server:name==='./flow.js'?flow:audio);await module.evaluate();
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const {f,interval} of intervals)if(system.currentTick%interval===0)f();}}
function spawn(e){dimension.entities.push(e);events.entitySpawn.emit({entity:e});}
function tap(e){events.playerInteractWithEntity.emit({target:e,player});}
const a=entity('a');spawn(a);
check('adapter only discovers its own entity type',()=>{const outsider=entity('other');outsider.typeId='minecraft:cow';spawn(outsider);tap(outsider);assert.equal(outsider.props.size,0);});
check('rehearsal initially dark and unloaded',()=>{assert.equal(a.props.get('kg_imm:lit'),false);assert.equal(a.props.get('kg_imm:loaded'),false);});
check('held item interactions never drive the lab',()=>{events.playerInteractWithEntity.emit({target:a,player,beforeItemStack:{typeId:'minecraft:stick'}});assert.equal(a.props.get('kg_imm:lit'),false);});
check('no empty-grill loop',()=>{tap(a);tick(3);assert.equal(a.props.get('kg_imm:lit'),true);assert.equal(player.sounds.length,0);});
check('insert loop starts once, not every tick',()=>{tap(a);tick(10);assert.equal(player.sounds.filter(s=>s.id==='kg_imm.grill_loop').length,1);});
check('burst clicks do not brush and flip together',()=>{tap(a);tap(a);assert.equal(a.props.get('kg_imm:action'),1);assert.equal(a.props.get('kg_imm:flips'),0);});
tick(20);
check('full-duration brush ends automatically',()=>assert.equal(a.props.get('kg_imm:action'),0));
for(let i=1;i<=4;i++){tap(a);tick(14);}
check('four turns before seasoning',()=>assert.equal(a.props.get('kg_imm:flips'),4));
tap(a);tick(10);tap(a);tick(3);
check('taking the last display sample stops loop',()=>assert.ok(player.stops.includes('stopsound @s kg_imm.grill_loop')));
tap(a);tick(4);
check('original eating recording starts once on dedicated scene channel',()=>assert.equal(player.sounds.filter(s=>s.id==='kg_imm.four_skewer_eat_ch0').length,1));
player.location.x=80;player.isSneaking=true;tap(a);tick(1);player.isSneaking=false;player.location.x=0;
check('cancelling meal stops its channel even after listener moved away',()=>{assert.ok(player.stops.includes('stopsound @s kg_imm.four_skewer_eat_ch0'));assert.equal(a.props.get('kg_imm:bites'),0);assert.equal(a.props.get('kg_imm:action'),0);});
const b=entity('b',2);spawn(b);tick(3);tap(b);tick(3);tap(b);tick(3);tap(b);tick(20);for(let i=0;i<4;i++){tap(b);tick(14)}tap(b);tick(10);tap(b);tick(3);tap(b);
check('second scene uses a separate eating channel',()=>assert.ok(player.sounds.some(s=>s.id==='kg_imm.four_skewer_eat_ch1')));
const mark=player.stops.length;tick(3);player.isSneaking=true;tap(a);player.isSneaking=false;
check('cancelling first scene never stops second scene channel',()=>assert.ok(!player.stops.slice(mark).includes('stopsound @s kg_imm.four_skewer_eat_ch1')));
b.isValid=false;tick(1);
check('unloaded entity cleans up audio without needing a valid location',()=>assert.ok(player.stops.includes('stopsound @s kg_imm.four_skewer_eat_ch1')));
check('commands are only scoped stopsound; no inventory/health/block effects',()=>assert.ok(player.stops.every(s=>/^stopsound @s kg_imm\./.test(s))));
check('adapter has no dependency on server UI or player skin replacement',()=>{const s=fs.readFileSync(new URL('./main.js',import.meta.url),'utf8');assert.ok(!s.includes('server-ui'));assert.ok(!s.includes('player.json'));});
console.log(JSON.stringify({passed:count,failed:0,scope:'actual adapter executed in mock event host; not a Minecraft/BDS test'}));
