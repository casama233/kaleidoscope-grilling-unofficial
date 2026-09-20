import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

let checks=0;const check=(n,f)=>{f();checks++;console.log('PASS',n)};
class ItemStack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.dp=new Map();this.lore=[];this.nameTag=undefined}
 get maxAmount(){return this.typeId.includes('skewer')||this.typeId==='kaleidoscope_grilling:dark_grilling'?64:1}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getDynamicProperty(k){return this.dp.get(k)}
 getDynamicPropertyIds(){return [...this.dp.keys()]}
 setLore(v){this.lore=[...v]}getLore(){return [...this.lore]}
 clone(){const s=new ItemStack(this.typeId,this.amount);s.dp=new Map(this.dp);s.lore=[...this.lore];s.nameTag=this.nameTag;return s}
 isStackableWith(o){return !!o&&this.typeId===o.typeId&&!this.dp.size&&!o.dp.size&&JSON.stringify(this.lore)===JSON.stringify(o.lore)}
}
class BlockPermutation{
 constructor(typeId,states={}){this.type={id:typeId};this.typeId=typeId;this.states={...states}}
 getState(k){return this.states[k]}
 withState(k,v){return new BlockPermutation(this.typeId,{...this.states,[k]:v})}
 static resolve(typeId,states={}){return new BlockPermutation(typeId,states)}
}
const EquipmentSlot={Offhand:'Offhand'},GameMode={Creative:'Creative',Survival:'Survival'};
class Container{
 constructor(size){this.slots=Array(size).fill(undefined);this.size=size}
 getItem(i){return this.slots[i]}setItem(i,v){this.slots[i]=v}
 addItem(stack){for(let i=0;i<this.size;i++){const t=this.slots[i];if(t&&t.isStackableWith(stack)&&t.amount<t.maxAmount){const m=Math.min(t.maxAmount-t.amount,stack.amount);t.amount+=m;if(m===stack.amount)return undefined;stack=stack.clone();stack.amount-=m}}const i=this.slots.findIndex(x=>!x);if(i<0)return stack;this.slots[i]=stack;return undefined}
}
const signal=()=>({listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e);return e}});
const afterNames=['itemStartUse','itemCompleteUse','itemStopUse','playerPlaceBlock','entityHitEntity'];
const beforeNames=['entityHurt','playerInteractWithBlock','playerBreakBlock','playerPlaceBlock'];
const afterEvents=Object.fromEntries(afterNames.map(n=>[n,signal()])),beforeEvents=Object.fromEntries(beforeNames.map(n=>[n,signal()]));
const blocks=new Map(),drops=[],particles=[],sounds=[],entities=[];
const posKey=p=>p.x+','+p.y+','+p.z;
class MockBlock{
 constructor(typeId,x,y,z,slots=0,solid=null){this.typeId=typeId;this.x=x;this.y=y;this.z=z;this.location={x,y,z};this.dimension=dimension;this.isValid=true;this._solid=solid;this._c=slots?new Container(slots):undefined;this.permutation=new BlockPermutation(typeId,this.defaults(typeId))}
 defaults(id){if(id==='kaleidoscope_grilling:grill')return {'minecraft:cardinal_direction':'north','kaleidoscope_grilling:legged':false,'kaleidoscope_grilling:lit':false};if(id.includes('_oil'))return {'kaleidoscope_grilling:level':0};return {}}
 get isSolid(){if(this._solid!==null)return this._solid;return this.typeId!=='minecraft:air'&&!this.typeId.includes('_oil')}
 getComponent(id){if(id==='minecraft:inventory'&&this._c)return {container:this._c}}
 setPermutation(p){this.permutation=p;this.typeId=p.typeId;blocks.set(posKey(this.location),this)}
 setType(id){this.typeId=id;this.permutation=new BlockPermutation(id,this.defaults(id));if(id==='minecraft:air')this._solid=false;blocks.set(posKey(this.location),this)}
 below(){return dimension.getBlock({x:this.x,y:this.y-1,z:this.z})}
}
const dimension={
 id:'minecraft:overworld',
 getBlock(p){const k=posKey(p);if(!blocks.has(k))blocks.set(k,new MockBlock('minecraft:air',p.x,p.y,p.z,0,false));return blocks.get(k)},
 spawnItem(stack,location){drops.push({stack,location});return {itemStack:stack}},
 playSound(id,location){sounds.push({id,location})},
 spawnParticle(id,location){particles.push({id,location})},
 getEntities(q){return entities.filter(e=>{if(q.type&&e.typeId!==q.type)return false;if(q.location&&q.maxDistance!==undefined){const dx=e.location.x-q.location.x,dy=e.location.y-q.location.y,dz=e.location.z-q.location.z;if(Math.hypot(dx,dy,dz)>q.maxDistance)return false}return true})}
};
function makeBlock(type,x,y=64,z=0,slots=0,solid=null){const b=new MockBlock(type,x,y,z,slots,solid);blocks.set(posKey(b.location),b);return b}
const inventory=new Container(36);let off;const effects=new Map(),pdp=new Map(),impulses=[],damageReplay=[];
const hunger={currentValue:10,effectiveMax:20,setCurrentValue(v){this.currentValue=v}},sat={currentValue:2,effectiveMax:20,setCurrentValue(v){this.currentValue=v}},hp={currentValue:20,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const player={id:'p1',typeId:'minecraft:player',selectedSlotIndex:0,isSneaking:false,isSprinting:false,location:{x:0,y:64,z:0},dimension,_velocity:{x:0,y:0,z:0},_standing:null,animations:[],
 getGameMode(){return GameMode.Survival},
 getComponent(id){if(id==='minecraft:inventory')return {container:inventory};if(id==='minecraft:equippable')return {getEquipment:s=>s===EquipmentSlot.Offhand?off:undefined,setEquipment(s,v){if(s===EquipmentSlot.Offhand)off=v;return true}};if(id==='minecraft:player.hunger')return hunger;if(id==='minecraft:player.saturation')return sat;if(id==='minecraft:health')return hp},
 getDynamicProperty:k=>pdp.get(k),setDynamicProperty(k,v){v===undefined?pdp.delete(k):pdp.set(k,v)},
 getEffects(){return [...effects.values()]},addEffect(id,duration,opt={}){effects.set(id,{typeId:id,duration,amplifier:opt.amplifier??0});if(id==='health_boost')hp.effectiveMax=20+(opt.amplifier??0)+1===2?28:24},removeEffect(id){effects.delete(id);if(id==='health_boost')hp.effectiveMax=20},
 getVelocity(){return {...this._velocity}},applyImpulse(v){impulses.push(v);this._velocity={x:this._velocity.x+(v.x??0),y:this._velocity.y+(v.y??0),z:this._velocity.z+(v.z??0)}},applyKnockback(){},
 getBlockStandingOn(){return this._standing},playAnimation(id){this.animations.push(id)},playSound(){},runCommand(){},getHeadLocation(){return {x:0,y:65.6,z:0}},getViewDirection(){return {x:0,y:0,z:1}},
 applyDamage(amount,opt){damageReplay.push({amount,opt});return true},onScreenDisplay:{setActionBar(){}}
};
function mob(type,x,y,z){const m={id:type+entities.length,typeId:type,location:{x,y,z},knocks:[],applyKnockback(v,h){this.knocks.push({v,h})}};entities.push(m);return m}
const wdp=new Map();const world={afterEvents,beforeEvents,getAllPlayers:()=>[player],getDimension:()=>dimension,getDynamicProperty:k=>wdp.get(k),setDynamicProperty(k,v){v===undefined?wdp.delete(k):wdp.set(k,v)},getAbsoluteTime:()=>80000+system.currentTick};
const intervals=[];const system={currentTick:0,run(f){f()},runInterval(f,n){intervals.push({f,n})}};
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const x of intervals)if(system.currentTick%x.n===0)x.f()}}
function hand(id,amount=1){inventory.setItem(0,id?new ItemStack(id,amount):undefined);return inventory.getItem(0)}
function place(b){afterEvents.playerPlaceBlock.emit({block:b,player})}
function interact(b,itemStack=inventory.getItem(0),face='Up'){const e={block:b,player,itemStack,blockFace:face,cancel:false};beforeEvents.playerInteractWithBlock.emit(e);return e}
const math=Object.create(Math);math.random=()=>.2;
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Error,Boolean,Math:math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const files=['main.js','data.js','core_logic.js','a23_hot_merge.js','a23_hot_runtime.js','a23_oil_world.js'];
const mods={};for(const n of files)mods[n]=new vm.SourceTextModule(fs.readFileSync(new URL(n,root),'utf8'),{context,identifier:n});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode','BlockPermutation'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',ItemStack);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode);this.setExport('BlockPermutation',BlockPermutation)},{context,identifier:'server'});
async function linker(spec){if(spec==='@minecraft/server')return server;return mods[spec.replace('./','')]}
await mods.main.link(linker);await mods.main.evaluate();
const hot=mods['a23_hot_runtime.js'].namespace;

// Hot stack manual merge.
const a=new ItemStack('kaleidoscope_grilling:grilled_beef_skewer',2),b=new ItemStack('kaleidoscope_grilling:grilled_beef_skewer',1);
a.setDynamicProperty('kaleidoscope_grilling:seasonings','[]');b.setDynamicProperty('kaleidoscope_grilling:seasonings','[]');
a.setDynamicProperty('kaleidoscope_grilling:hot_until',world.getAbsoluteTime()+1200);b.setDynamicProperty('kaleidoscope_grilling:hot_until',world.getAbsoluteTime()+600);
const c=new Container(4);c.setItem(0,a);hot.mergeIntoContainer(c,b,world.getAbsoluteTime());
check('manual hot merge makes amount 3 with weighted remaining heat',()=>{assert.equal(c.getItem(0).amount,3);assert.equal(c.getItem(0).getDynamicProperty('kaleidoscope_grilling:hot_until')-world.getAbsoluteTime(),1000)});

// Storage normal sort interaction.
const chest=makeBlock('minecraft:chest',5,64,0,27,true),s1=new ItemStack('kaleidoscope_grilling:grilled_fish_skewer',1),s2=new ItemStack('kaleidoscope_grilling:grilled_fish_skewer',1);
s1.setDynamicProperty('kaleidoscope_grilling:seasonings','[]');s2.setDynamicProperty('kaleidoscope_grilling:seasonings','[]');s1.setDynamicProperty('kaleidoscope_grilling:hot_until',world.getAbsoluteTime()+7000);s2.setDynamicProperty('kaleidoscope_grilling:hot_until',world.getAbsoluteTime()+2000);chest._c.setItem(0,s1);chest._c.setItem(5,s2);hand();player.isSneaking=true;interact(chest,undefined);player.isSneaking=false;
check('sneak-empty chest sort merges hot skewers within five-minute window',()=>assert.equal(chest._c.slots.filter(Boolean).find(x=>x.typeId.includes('fish_skewer')).amount,2));

// Grill state: unsupported -> legged, light -> lit, support -> flat.
const below=makeBlock('minecraft:air',0,63,0,0,false),grill=makeBlock('kaleidoscope_grilling:grill',0,64,0,3,false);place(grill);
check('placed grill without support becomes legged',()=>assert.equal(grill.permutation.getState('kaleidoscope_grilling:legged'),true));
hand('minecraft:flint_and_steel');interact(grill);
check('lit grill permutation tracks gameplay lit state',()=>assert.equal(grill.permutation.getState('kaleidoscope_grilling:lit'),true));
below.setType('minecraft:stone');below._solid=true;tick(1);
check('adding solid support switches same grill block to flat',()=>assert.equal(grill.permutation.getState('kaleidoscope_grilling:legged'),false));

// Dragon Blood exact effective +6 via native +4 plus virtual 2.
pdp.set('kaleidoscope_grilling:a21_fx',JSON.stringify({dragon_blood:{until:world.getAbsoluteTime()+1000,amp:0}}));pdp.set('kaleidoscope_grilling:dragon_pool',2);
const hurt1={hurtEntity:player,damage:1,damageSource:{cause:'entityAttack'},cancel:false};beforeEvents.entityHurt.emit(hurt1);
check('Dragon Blood virtual 2 HP absorbs first damage exactly',()=>{assert.equal(hurt1.cancel,true);assert.equal(pdp.get('kaleidoscope_grilling:dragon_pool'),1)});
const hurt2={hurtEntity:player,damage:3,damageSource:{cause:'entityAttack'},cancel:false};beforeEvents.entityHurt.emit(hurt2);
check('Dragon Blood replays only damage beyond remaining virtual pool',()=>{assert.equal(hurt2.cancel,true);assert.equal(damageReplay.at(-1).amount,2)});

// Effect refinements.
player._standing=makeBlock('minecraft:snow_block',20,63,0,0,true);player._velocity={x:1,y:0,z:0};pdp.set('kaleidoscope_grilling:a21_fx',JSON.stringify({tundra_strider:{until:world.getAbsoluteTime()+1000,amp:0}}));tick(1);
check('Tundra Strider snow-like factor adds 30 percent horizontal impulse',()=>assert.ok(impulses.some(v=>Math.abs((v.x??0)-.3)<.0001)));
const creeper=mob('minecraft:creeper',3,64,0),phantom=mob('minecraft:phantom',5,74,0);pdp.set('kaleidoscope_grilling:a21_fx',JSON.stringify({mustard:{until:world.getAbsoluteTime()+1000,amp:0},sulfur:{until:world.getAbsoluteTime()+1000,amp:0}}));tick(5);
check('Mustard keeps creeper flee radius 6',()=>assert.ok(creeper.knocks.length>0));
check('Sulfur uses 8 horizontal / 16 vertical AABB-like filter',()=>assert.ok(phantom.knocks.length>0));

// Scripted world oil source/flow and pot transfer.
const stone=makeBlock('minecraft:stone',30,64,0,0,true);hand('kaleidoscope_grilling:canola_oil_bucket');interact(stone,inventory.getItem(0),'Up');
const source=dimension.getBlock({x:30,y:65,z:0});
check('oil bucket places a level-0 world source and returns empty bucket',()=>{assert.equal(source.typeId,'kaleidoscope_grilling:canola_oil');assert.equal(source.permutation.getState('kaleidoscope_grilling:level'),0);assert.equal(inventory.getItem(0).typeId,'minecraft:bucket')});
tick(6);
check('canola source spreads horizontally when downward path is blocked',()=>assert.equal(dimension.getBlock({x:31,y:65,z:0}).typeId,'kaleidoscope_grilling:canola_oil'));
hand('minecraft:bucket');interact(source,inventory.getItem(0),'Up');
check('empty bucket collects source as canola oil bucket',()=>assert.equal(inventory.getItem(0).typeId,'kaleidoscope_grilling:canola_oil_bucket'));
tick(6);
check('removing source cleans its generated flowing cells',()=>assert.equal(dimension.getBlock({x:31,y:65,z:0}).typeId,'minecraft:air'));

hand('kaleidoscope_grilling:secret_chili_oil_bucket');interact(stone,inventory.getItem(0),'Up');const secret=dimension.getBlock({x:30,y:65,z:0});hand('kaleidoscope_cookery:oil_pot');interact(secret,inventory.getItem(0),'Up');
check('Cookery empty pot fills from world oil source with 256 count and type',()=>{const p=inventory.getItem(0);assert.equal(p.typeId,'kaleidoscope_cookery:oil_pot_filled');assert.equal(p.getDynamicProperty('kc_oil_count'),256);assert.equal(p.getDynamicProperty('kaleidoscope_grilling:oil_type'),'secret_chili')});

console.log(JSON.stringify({passed:checks,failed:0,scope:'A2.3 generated runtime: hot stacking/storage sort, grill visual states, refined effects and scripted world oils; not Minecraft/BDS engine acceptance'}));
