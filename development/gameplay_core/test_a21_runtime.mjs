import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

let checks=0;const check=(name,fn)=>{fn();checks++;console.log('PASS '+name)};
class ItemStack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.dp=new Map();this.lore=[]}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getDynamicProperty(k){return this.dp.get(k)}
 setLore(v){this.lore=[...v]}
 getLore(){return [...this.lore]}
}
const EquipmentSlot={Offhand:'Offhand'},GameMode={Creative:'Creative',Survival:'Survival'};
class Container{
 constructor(size){this.slots=Array(size).fill(undefined)}
 getItem(i){return this.slots[i]}
 setItem(i,v){this.slots[i]=v}
 addItem(stack){const i=this.slots.findIndex(x=>!x);if(i<0)return stack;this.slots[i]=stack;return undefined}
}
const signal=()=>({listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e);return e}});
const afterNames=['itemStartUse','itemCompleteUse','itemStopUse','playerPlaceBlock','entityHitEntity'];
const beforeNames=['entityHurt','playerInteractWithBlock','playerBreakBlock','playerPlaceBlock'];
const afterEvents=Object.fromEntries(afterNames.map(n=>[n,signal()])),beforeEvents=Object.fromEntries(beforeNames.map(n=>[n,signal()]));
const blocks=new Map(),drops=[],sounds=[],particles=[],entities=[];
const bkey=p=>p.x+','+p.y+','+p.z;
const dimension={
 id:'minecraft:overworld',
 getBlock(p){return blocks.get(bkey(p))},
 spawnItem(stack,location){drops.push({stack,location});return {itemStack:stack}},
 playSound(id,location){sounds.push({id,location})},
 spawnParticle(id,location){particles.push({id,location})},
 getEntities(q){return entities.filter(e=>(!q.type||e.typeId===q.type))}
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
const effects=new Map(),pdp=new Map();let killed=false,teleports=0,impulses=0;
const player={id:'p1',typeId:'minecraft:player',selectedSlotIndex:0,isSneaking:false,isSprinting:false,location:{x:0,y:64,z:-1},dimension,animations:[],messages:[],
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
 applyImpulse(){impulses++},applyKnockback(){},tryTeleport(){teleports++;return true},kill(){killed=true;return true},applyDamage(){killed=true;return true},
 getBlockStandingOn(){return makeBlock('minecraft:snow_block',99,99)},
 onScreenDisplay:{setActionBar(t){player.messages.push(t)}}
};
const targetEffects=new Map();
const target={id:'target',typeId:'minecraft:zombie',location:{x:2,y:64,z:0},dimension,addEffect(id,duration,opt={}){targetEffects.set(id,{duration,amplifier:opt.amplifier??0})},applyKnockback(){}};
const wdp=new Map();
const world={afterEvents,beforeEvents,getAllPlayers:()=>[player],getDimension:()=>dimension,getDynamicProperty:k=>wdp.get(k),setDynamicProperty(k,v){v===undefined?wdp.delete(k):wdp.set(k,v)},getAbsoluteTime:()=>50000+system.currentTick};
const intervals=[];
const system={currentTick:0,run(f){f()},runInterval(f,n){intervals.push({f,n})}};
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const x of intervals)if(system.currentTick%x.n===0)x.f()}}
function hand(id,amount=1){inventory.setItem(0,id?new ItemStack(id,amount):undefined);return inventory.getItem(0)}
function interact(block){const e={block,player,cancel:false};beforeEvents.playerInteractWithBlock.emit(e);return e}
function place(block){afterEvents.playerPlaceBlock.emit({block,player})}
function itemComplete(stack){afterEvents.itemCompleteUse.emit({source:player,itemStack:stack})}
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Error,Boolean,Math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const mods={};
for(const n of ['main.js','data.js','core_logic.js'])mods[n]=new vm.SourceTextModule(fs.readFileSync(new URL(n,root),'utf8'),{context,identifier:n});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',ItemStack);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode)},{context,identifier:'server'});
async function linker(spec){if(spec==='@minecraft/server')return server;return mods[spec.replace('./','')]}
await mods['main.js'].link(linker);await mods['main.js'].evaluate();

const bottle=makeBlock('kaleidoscope_grilling:seasoning_bottle',-2,0);place(bottle);
for(const id of ['kaleidoscope_grilling:green_chili_powder','kaleidoscope_grilling:onion_powder','kaleidoscope_grilling:sichuan_pepper','kaleidoscope_grilling:sichuan_pepper','kaleidoscope_grilling:sichuan_pepper','kaleidoscope_grilling:sichuan_pepper','minecraft:redstone','minecraft:redstone']){hand(id);interact(bottle)}
hand();interact(bottle);
const pending=inventory.getItem(0);
check('8 ingredients return a pending seasoning bottle',()=>{assert.equal(pending.typeId,'kaleidoscope_grilling:pending_seasoning');assert.equal(JSON.parse(pending.getDynamicProperty('kaleidoscope_grilling:seasonings')).length,8)});
afterEvents.itemStartUse.emit({source:player,itemStack:pending});tick(80);itemComplete(pending);
const special=inventory.getItem(0);
check('80 tick shake creates special seasoning and preserves payload',()=>{assert.equal(special.typeId,'kaleidoscope_grilling:special_seasoning');assert.equal(JSON.parse(special.getDynamicProperty('kaleidoscope_grilling:seasonings')).length,8);assert.equal(special.getDynamicProperty('kaleidoscope_grilling:uses'),0)});

const grill=makeBlock('kaleidoscope_grilling:grill',0,0,3);place(grill);
hand('minecraft:flint_and_steel');interact(grill);
for(const id of ['raw_beef_skewer','raw_fish_skewer','raw_lamb_skewer']){hand('kaleidoscope_grilling:'+id);interact(grill)}
const pot=hand('kaleidoscope_cookery:oil_pot_filled');pot.setDynamicProperty('kc_oil_count',10);pot.setLore(['§7Oil: 10/256']);interact(grill);
check('Cookery filled oil pot consumes one point per occupied skewer',()=>{const h=inventory.getItem(0);assert.equal(h.typeId,'kaleidoscope_cookery:oil_pot_filled');assert.equal(h.getDynamicProperty('kc_oil_count'),7)});
for(let i=0;i<4;i++){hand();interact(grill);if(i<3)tick(20)}
inventory.setItem(0,special);interact(grill);
check('seasoning consumes three uses for three skewers',()=>assert.equal(inventory.getItem(0).getDynamicProperty('kaleidoscope_grilling:uses'),3));
const persisted=JSON.parse(wdp.get('kaleidoscope_grilling:g_minecraft_overworld_p0_p64_p0'));
check('grill persists exact seasoning ingredient payload',()=>assert.equal(persisted.seasonings.length,8));
hand();player.isSneaking=true;interact(grill);player.isSneaking=false;
const beef=inventory.slots.find(x=>x?.typeId==='kaleidoscope_grilling:grilled_beef_skewer');
check('cooked skewer stores absolute bucketed hot expiry',()=>{const u=beef.getDynamicProperty('kaleidoscope_grilling:hot_until');assert.ok(u>world.getAbsoluteTime());assert.equal(u%100,0)});
check('cooked skewer stores seasoning payload',()=>assert.equal(JSON.parse(beef.getDynamicProperty('kaleidoscope_grilling:seasonings')).length,8));

inventory.setItem(0,beef);hunger.currentValue=10;saturation.currentValue=2;effects.clear();
afterEvents.itemStartUse.emit({source:player,itemStack:beef});tick(25);afterEvents.itemStopUse.emit({source:player,itemStack:beef});
check('hot early settlement keeps nutrition and applies 125 percent saturation',()=>{assert.equal(hunger.currentValue,15);assert.equal(saturation.currentValue,9.5)});
check('hot fixed beef strength is doubled before seasoning',()=>assert.equal(effects.get('strength').duration,400));
check('seasoning redstone adds speed without hot-duration doubling',()=>assert.equal(effects.get('speed').duration,3600));
check('four Sichuan pepper portions activate tracked numb effect',()=>{const fx=JSON.parse(pdp.get('kaleidoscope_grilling:a21_fx'));assert.ok(fx.numb.until>world.getAbsoluteTime())});

const pork=hand('kaleidoscope_grilling:grilled_pork_belly_skewer');itemComplete(pork);
check('Cookery vigor semantic layer is granted from pork belly',()=>assert.ok(JSON.parse(pdp.get('kaleidoscope_grilling:a21_fx')).vigor));
player.isSprinting=true;tick(1);hunger.currentValue=8;tick(1);
check('vigor restores hunger lost while sprinting',()=>assert.ok(hunger.currentValue>8));

const slime=hand('kaleidoscope_grilling:grilled_slime_skewer');itemComplete(slime);
afterEvents.entityHitEntity.emit({damagingEntity:player,hitEntity:target});
check('hinder gives Slowness II for 100 ticks on hit',()=>assert.deepEqual(targetEffects.get('slowness'),{duration:100,amplifier:1}));

const ender=hand('kaleidoscope_grilling:grilled_ender_pearl_skewer');itemComplete(ender);
const hurt={hurtEntity:player,damage:5,damageSource:{cause:'projectile',damagingProjectile:{typeId:'minecraft:arrow'}},cancel:false};beforeEvents.entityHurt.emit(hurt);
check('projectile dodge cancels projectile damage and teleports',()=>{assert.equal(hurt.cancel,true);assert.ok(teleports>0)});

const golden=hand('kaleidoscope_grilling:grilled_golden_skewer');itemComplete(golden);
check('golden skewer grants absolute-time invincible state',()=>assert.ok(JSON.parse(pdp.get('kaleidoscope_grilling:a21_fx')).invincible));
const ordinary=hand('kaleidoscope_grilling:ordinary_skewer');itemComplete(ordinary);
check('ordinary skewer consumes invincible challenge without guaranteed death',()=>{assert.equal(JSON.parse(pdp.get('kaleidoscope_grilling:a21_fx')??'{}').invincible,undefined);assert.equal(killed,false)});
const ordinary2=hand('kaleidoscope_grilling:ordinary_skewer');itemComplete(ordinary2);
check('ordinary skewer without invincible kills the eater',()=>assert.equal(killed,true));

console.log(JSON.stringify({passed:checks,failed:0,scope:'A2.1 generated runtime with Cookery oil, seasoning, hot food and selected semantic effects; not Minecraft engine acceptance'}));
