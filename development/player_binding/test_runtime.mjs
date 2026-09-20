import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
let checks=0;const check=(name,fn)=>{fn();checks++;console.log('PASS',name);};
const eventNames=['entitySpawn','playerInteractWithEntity','playerSpawn'];
const events=Object.fromEntries(eventNames.map(k=>[k,{listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e)}}]));
const intervals=[],warnings=[];
const dimension={id:'minecraft:overworld',entities:[],getEntities:()=>dimension.entities,playSound(){},spawnParticle(){}};
class ItemStack{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;}}
const EquipmentSlot={Mainhand:'Mainhand',Offhand:'Offhand'};
const slots=Array(9).fill(undefined);let off;
const container={getItem:i=>slots[i],setItem(i,v){slots[i]=v}};
const eq={getEquipment(s){return s===EquipmentSlot.Offhand?off:slots[player.selectedSlotIndex]},setEquipment(s,v){if(s===EquipmentSlot.Offhand)off=v;else slots[player.selectedSlotIndex]=v;return true}};
const dyn=new Map();
const player={id:'player1',isSneaking:false,selectedSlotIndex:0,dimension,location:{x:0,y:0,z:0},animations:[],sounds:[],stops:[],
 getComponent(id){return id==='minecraft:equippable'?eq:id==='minecraft:inventory'?{container}:undefined},
 getViewDirection(){return {x:0,y:0,z:1}},getDynamicProperty:k=>dyn.get(k),setDynamicProperty(k,v){v===undefined?dyn.delete(k):dyn.set(k,v)},
 playAnimation(id,opt){this.animations.push({id,opt,tick:system.currentTick})},playSound(id,opt){this.sounds.push({id,opt,tick:system.currentTick})},
 runCommand(s){assert.match(s,/^stopsound @s kg_imm\.[a-z0-9_]+$/);this.stops.push(s)},onScreenDisplay:{setActionBar(){}}
};
const world={afterEvents:events,getAllPlayers:()=>[player],getDimension:()=>dimension};
const system={currentTick:0,run(f){f()},runInterval(f,interval){intervals.push({f,interval})}};
function entity(id,z=1){const data=new Map(),props=new Map();return {id,typeId:'kg_imm:rehearsal',isValid:true,location:{x:0,y:0,z},dimension,props,data,getDynamicProperty:k=>data.get(k),setDynamicProperty:(k,v)=>data.set(k,v),setProperty:(k,v)=>props.set(k,v)}}
const math=Object.create(Math);math.random=()=>.2;
const ctx=vm.createContext({console:{warn:(...x)=>warnings.push(x)},Math:math,JSON,Map,Set,Object,Array,Number,String,Error,Boolean});
const root=new URL('../../projects/grilling/integration/immersion_lab/behavior_pack/scripts/',import.meta.url);
const sources={};
for(const n of ['main.js','flow.js','audio.js','profile_rules.js','player_binding.js'])sources[n]=new vm.SourceTextModule(fs.readFileSync(new URL(n,root),'utf8'),{context:ctx,identifier:n});
const server=new vm.SyntheticModule(['world','system','EquipmentSlot','ItemStack'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('ItemStack',ItemStack)},{context:ctx,identifier:'server'});
async function linker(spec,mod){if(spec==='@minecraft/server')return server;const n=spec.replace('./','');return sources[n];}
await sources['main.js'].link(linker);await sources['main.js'].evaluate();
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const {f,interval} of intervals)if(system.currentTick%interval===0)f();}}
function spawn(e){dimension.entities.push(e);events.entitySpawn.emit({entity:e});}
function tap(e){events.playerInteractWithEntity.emit({target:e,player});}
function held(id,hand='main'){if(hand==='main')slots[player.selectedSlotIndex]=id?new ItemStack(id):undefined;else off=id?new ItemStack(id):undefined;}
const a=entity('a');spawn(a);
check('ignite empty hand',()=>{tap(a);tick(3);assert.equal(a.props.get('kg_imm:lit'),true);});
check('insert uses reach animation',()=>{tap(a);assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.reach.main'));tick(3);});
held('kg_imm:oil_brush','off');
check('offhand brush is accepted only in calibrated stance',()=>{tap(a);assert.equal(a.props.get('kg_imm:action'),1);assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.brush.off'));});
tick(3);
check('brush contact cue is delayed until pickup finishes',()=>assert.ok(player.sounds.some(x=>x.id==='kg_imm.grill_flip'&&x.tick>=9)));
tick(23);held();held(null,'off');
for(let i=0;i<4;i++){tap(a);tick(14)}
held('kg_imm:seasoning_bottle','main');
check('mainhand seasoning binding runs',()=>{tap(a);assert.equal(a.props.get('kg_imm:action'),3);assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.season.main'));});
tick(16);held();tap(a);tick(3);
held('kg_imm:eat_three_random','main');
check('THREE_RANDOM resolves once to THREE with deterministic random',()=>{tap(a);assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.eat_three.main'));assert.equal(slots[0].typeId,'kg_imm:visual_0');assert.equal(off?.typeId,'kg_imm:bite_piece');});
tick(20);
check('first THREE bite swaps the active-hand visual',()=>assert.equal(slots[0].typeId,'kg_imm:visual_1'));
tick(80);
check('end restores selector and helper hand',()=>{assert.equal(slots[0].typeId,'kg_imm:eat_three_random');assert.equal(off,undefined);});
const b=entity('b');spawn(b);tick(3);
held();held(null,'off');tap(b);tick(3);tap(b);tick(3);held('kg_imm:oil_brush');tap(b);tick(26);held();for(let i=0;i<4;i++){tap(b);tick(14)}held('kg_imm:seasoning_bottle');tap(b);tick(16);held();tap(b);tick(3);
held('kg_imm:eat_two','off');
check('fresh stand reached taken phase',()=>assert.equal(JSON.parse(b.data.get('kg_imm:rehearsal_state')).phase,'taken'));
check('selector resolves occupied offhand',()=>assert.equal(sources['player_binding.js'].namespace.selector(player).name,'off'));
check('offhand eating uses left item/arm animation',()=>{tap(b);assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.eat_two.off'));assert.equal(off.typeId,'kg_imm:visual_0');});
player.isSneaking=true;tap(b);player.isSneaking=false;
check('cancel restores offhand selector',()=>assert.equal(off.typeId,'kg_imm:eat_two'));
held(null,'off');held('kg_imm:eat_four','main');tap(b);
check('restore token exists while visual replacement is active',()=>assert.equal(typeof dyn.get('kg_imm:eat_restore'),'string'));
events.playerSpawn.emit({initialSpawn:true,player});
check('spawn recovery restores selector without overwriting other inventory',()=>{assert.equal(slots[0].typeId,'kg_imm:eat_four');assert.equal(dyn.has('kg_imm:eat_restore'),false);});
check('no player resource override is used',()=>{const p=new URL('../../projects/grilling/integration/immersion_lab/resource_pack/entity/player.entity.json',import.meta.url);assert.equal(fs.existsSync(p),false);});
console.log(JSON.stringify({passed:checks,failed:0,scope:'actual A1.16 adapter in mock event host; not Minecraft/BDS acceptance'}));
