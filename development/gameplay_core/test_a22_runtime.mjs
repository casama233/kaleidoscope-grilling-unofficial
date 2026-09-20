import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

let checks=0;const check=(name,fn)=>{fn();checks++;console.log('PASS '+name)};
class ItemStack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.dp=new Map();this.lore=[]}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getDynamicProperty(k){return this.dp.get(k)}
 setLore(v){this.lore=[...v]} getLore(){return [...this.lore]}
}
const EquipmentSlot={Offhand:'Offhand'},GameMode={Creative:'Creative',Survival:'Survival'};
class Container{
 constructor(size){this.slots=Array(size).fill(undefined)}
 getItem(i){return this.slots[i]} setItem(i,v){this.slots[i]=v}
 addItem(stack){const i=this.slots.findIndex(x=>!x);if(i<0)return stack;this.slots[i]=stack;return undefined}
}
const signal=()=>({listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e);return e}});
const afterNames=['itemStartUse','itemCompleteUse','itemStopUse','playerPlaceBlock','entityHitEntity'];
const beforeNames=['entityHurt','playerInteractWithBlock','playerBreakBlock','playerPlaceBlock'];
const afterEvents=Object.fromEntries(afterNames.map(n=>[n,signal()])),beforeEvents=Object.fromEntries(beforeNames.map(n=>[n,signal()]));
const blocks=new Map(),drops=[],sounds=[],particles=[],commands=[];
const bkey=p=>p.x+','+p.y+','+p.z;
const dimension={
 id:'minecraft:overworld',
 getBlock(p){return blocks.get(bkey(p))},
 spawnItem(stack,location){drops.push({stack,location});return {itemStack:stack}},
 playSound(id,location){sounds.push({id,location,kind:'dimension'})},
 spawnParticle(id,location){particles.push({id,location})},
 getEntities(){return []}
};
function makeBlock(typeId,x,z=0,slots=0){
 const c=slots?new Container(slots):undefined;
 const b={typeId,x,y:64,z,location:{x,y:64,z},dimension,isValid:true,permutation:{getState(){return false}},
  getComponent(id){if(id==='minecraft:inventory'&&c)return {container:c}},
  setType(id){this.typeId=id;if(id==='minecraft:air')blocks.delete(bkey(this.location))},_c:c};
 blocks.set(bkey(b.location),b);return b;
}
const inventory=new Container(36);let off;
const hunger={currentValue:10,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const saturation={currentValue:2,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const health={currentValue:20,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const effects=new Map(),pdp=new Map();let randomValue=.8;
const player={id:'p1',typeId:'minecraft:player',selectedSlotIndex:0,isSneaking:false,isSprinting:false,location:{x:0,y:64,z:-1},dimension,animations:[],messages:[],playedSounds:[],
 getGameMode(){return GameMode.Survival},
 getComponent(id){
  if(id==='minecraft:inventory')return {container:inventory};
  if(id==='minecraft:equippable')return {getEquipment:s=>s===EquipmentSlot.Offhand?off:undefined,setEquipment(s,v){if(s===EquipmentSlot.Offhand)off=v;return true}};
  if(id==='minecraft:player.hunger')return hunger;if(id==='minecraft:player.saturation')return saturation;if(id==='minecraft:health')return health;
 },
 addEffect(id,duration,opt={}){effects.set(id,{typeId:id,duration,amplifier:opt.amplifier??0,isValid:true})},
 removeEffect(id){effects.delete(id)},getEffects(){return [...effects.values()]},
 getDynamicProperty:k=>pdp.get(k),setDynamicProperty(k,v){v===undefined?pdp.delete(k):pdp.set(k,v)},
 playAnimation(id,opt){this.animations.push({id,opt,tick:system.currentTick})},
 playSound(id,opt){this.playedSounds.push({id,opt,tick:system.currentTick})},
 runCommand(cmd){commands.push({cmd,tick:system.currentTick});return {successCount:1}},
 getHeadLocation(){return {x:this.location.x,y:this.location.y+1.62,z:this.location.z}},
 getViewDirection(){return {x:0,y:0,z:1}},
 applyImpulse(){},applyKnockback(){},tryTeleport(){return true},kill(){return true},applyDamage(){return true},
 getBlockStandingOn(){return undefined},
 onScreenDisplay:{setActionBar(t){player.messages.push(t)}}
};
const wdp=new Map();
const world={afterEvents,beforeEvents,getAllPlayers:()=>[player],getDimension:()=>dimension,getDynamicProperty:k=>wdp.get(k),setDynamicProperty(k,v){v===undefined?wdp.delete(k):wdp.set(k,v)},getAbsoluteTime:()=>70000+system.currentTick};
const intervals=[];const system={currentTick:0,run(f){f()},runInterval(f,n){intervals.push({f,n})}};
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const x of intervals)if(system.currentTick%x.n===0)x.f()}}
function hand(id,amount=1){inventory.setItem(0,id?new ItemStack(id,amount):undefined);return inventory.getItem(0)}
function interact(block){const e={block,player,cancel:false};beforeEvents.playerInteractWithBlock.emit(e);return e}
function place(block){afterEvents.playerPlaceBlock.emit({block,player})}
const math=Object.create(Math);math.random=()=>randomValue;
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Error,Boolean,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const mods={};
for(const n of ['main.js','data.js','core_logic.js'])mods[n]=new vm.SourceTextModule(fs.readFileSync(new URL(n,root),'utf8'),{context,identifier:n});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',ItemStack);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode)},{context,identifier:'server'});
async function linker(spec){if(spec==='@minecraft/server')return server;return mods[spec.replace('./','')]}
await mods['main.js'].link(linker);await mods['main.js'].evaluate();

// Four physical bottles with independent payloads.
const bottle=makeBlock('kaleidoscope_grilling:seasoning_bottle_1',-2,0);place(bottle);
const p1=hand('kaleidoscope_grilling:pending_seasoning');p1.setDynamicProperty('kaleidoscope_grilling:seasonings',JSON.stringify(['kaleidoscope_grilling:green_chili_powder','kaleidoscope_grilling:onion_powder','kaleidoscope_grilling:sichuan_pepper']));interact(bottle);
const s2=hand('kaleidoscope_grilling:special_seasoning');s2.setDynamicProperty('kaleidoscope_grilling:seasonings',JSON.stringify(['minecraft:redstone']));s2.setDynamicProperty('kaleidoscope_grilling:uses',5);s2.setDynamicProperty('kaleidoscope_grilling:variant',6);interact(bottle);
hand('kaleidoscope_grilling:empty_seasoning_bottle');interact(bottle);
check('four bottle pushes select the four-bottle physical block',()=>assert.equal(bottle.typeId,'kaleidoscope_grilling:seasoning_bottle_4'));
const bottleKey='kaleidoscope_grilling:sb_minecraft_overworld_m2_p64_p0';
check('four bottle payloads are independently persisted',()=>{const v=JSON.parse(wdp.get(bottleKey));assert.equal(v.length,4);assert.equal(v[1].kind,'pending');assert.equal(v[2].kind,'special');assert.equal(v[2].uses,5);assert.equal(v[2].variant,6)});
hand();interact(bottle);
check('popping top bottle returns to three-bottle visual',()=>{assert.equal(bottle.typeId,'kaleidoscope_grilling:seasoning_bottle_3');assert.equal(inventory.getItem(0).typeId,'kaleidoscope_grilling:empty_seasoning_bottle')});
hand();interact(bottle);
check('popping special bottle preserves independent uses and variant',()=>{const s=inventory.getItem(0);assert.equal(s.typeId,'kaleidoscope_grilling:special_seasoning');assert.equal(s.getDynamicProperty('kaleidoscope_grilling:uses'),5);assert.equal(s.getDynamicProperty('kaleidoscope_grilling:variant'),6)});

// Oil type contract drives the actual grill heat duration.
const grill=makeBlock('kaleidoscope_grilling:grill',0,0,3);place(grill);
hand('minecraft:flint_and_steel');interact(grill);
hand('kaleidoscope_grilling:raw_beef_skewer');interact(grill);
const pot=hand('kaleidoscope_cookery:oil_pot_filled');pot.setDynamicProperty('kc_oil_count',8);pot.setDynamicProperty('kaleidoscope_grilling:oil_type','secret_chili');interact(grill);
const grillState=JSON.parse(wdp.get('kaleidoscope_grilling:g_minecraft_overworld_p0_p64_p0'));
check('secret chili oil type contract selects 12000 tick heat',()=>assert.equal(grillState.heatTicks,12000));

// Exact profile sound and bite particles share the same timeline.
const beef=hand('kaleidoscope_grilling:grilled_beef_skewer');
afterEvents.itemStartUse.emit({source:player,itemStack:beef});
check('FOUR profile starts the original four-skewer sound track',()=>assert.equal(player.playedSounds.at(-1).id,'kg_imm.four_skewer_eat'));
tick(19);
check('no bite crumb appears before the first authored bite point',()=>assert.equal(particles.filter(x=>x.id==='kaleidoscope_grilling:skewer_crumb').length,0));
tick(1);
check('first authored bite point emits five custom crumbs',()=>assert.equal(particles.filter(x=>x.id==='kaleidoscope_grilling:skewer_crumb').length,5));
tick(63);
check('all four FOUR-profile bite points emit exactly twenty crumbs',()=>assert.equal(particles.filter(x=>x.id==='kaleidoscope_grilling:skewer_crumb').length,20));
afterEvents.itemStopUse.emit({source:player,itemStack:beef});
check('stopping the meal stops its exact profile sound',()=>assert.ok(commands.some(x=>x.cmd==='stopsound @s kg_imm.four_skewer_eat')));

// THREE_RANDOM can now use a 5s native item while THREE_ALT still settles at 90 ticks.
randomValue=.8;hunger.currentValue=10;saturation.currentValue=2;
const lamb=hand('kaleidoscope_grilling:grilled_lamb_skewer');
afterEvents.itemStartUse.emit({source:player,itemStack:lamb});
tick(90);
check('THREE_RANDOM selected THREE_ALT settles at 90 ticks without waiting for 5s native completion',()=>{assert.equal(inventory.getItem(0),undefined);assert.equal(hunger.currentValue,18);assert.ok(commands.some(x=>x.cmd==='stopsound @s kg_imm.three_skewer_eat'))});

// Numb visual refreshes the limb animation without touching crosshair/UI.
pdp.set('kaleidoscope_grilling:a21_fx',JSON.stringify({numb:{until:world.getAbsoluteTime()+500,amp:0}}));
tick(12);
check('active Numb refreshes the A2.2 player limb animation',()=>assert.ok(player.animations.some(x=>x.id==='animation.kg_a22.player.numb')));

console.log(JSON.stringify({passed:checks,failed:0,scope:'A2.2 runtime: four-bottle payload stack, typed oil heat, bite sound/particles, THREE_RANDOM 90/100 timing, Numb limbs; not Minecraft engine acceptance'}));
