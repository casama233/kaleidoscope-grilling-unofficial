import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

let checks=0;const check=(n,f)=>{f();checks++;console.log('PASS',n)};
class ItemStack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.dp=new Map();}
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)}
 getDynamicProperty(k){return this.dp.get(k)}
}
const EquipmentSlot={Offhand:'Offhand'};
const GameMode={Creative:'Creative',Survival:'Survival'};
class Container{
 constructor(size){this.slots=Array(size).fill(undefined)}
 getItem(i){return this.slots[i]}
 setItem(i,v){this.slots[i]=v}
 addItem(stack){const empty=this.slots.findIndex(x=>!x);if(empty<0)return stack;this.slots[empty]=stack;return undefined}
}
const afterNames=['itemStartUse','itemCompleteUse','itemStopUse','playerPlaceBlock'];
const beforeNames=['entityHurt','playerInteractWithBlock','playerBreakBlock'];
const signal=()=>({listeners:[],subscribe(f){this.listeners.push(f)},emit(e){for(const f of this.listeners)f(e);return e}});
const afterEvents=Object.fromEntries(afterNames.map(n=>[n,signal()])),beforeEvents=Object.fromEntries(beforeNames.map(n=>[n,signal()]));
const blocks=new Map(),drops=[],sounds=[],particles=[];
const locKey=p=>p.x+','+p.y+','+p.z;
const dimension={id:'minecraft:overworld',getBlock(p){return blocks.get(locKey(p))},spawnItem(stack,location){drops.push({stack,location});return {itemStack:stack}},playSound(id,location){sounds.push({id,location})},spawnParticle(id,location){particles.push({id,location})}};
function makeBlock(x,z=0){
 const d=new Map(),container=new Container(3);
 const b={typeId:'kaleidoscope_grilling:grill',x,y:64,z,location:{x,y:64,z},dimension,isValid:true,
  getComponent(id){if(id==='minecraft:dynamic_properties')return {get:k=>d.get(k),set:(k,v)=>v===undefined?d.delete(k):d.set(k,v)};if(id==='minecraft:inventory')return {container}},
  setType(id){this.typeId=id;if(id==='minecraft:air')blocks.delete(locKey(this.location))},
  _d:d,_c:container};
 blocks.set(locKey(b.location),b);return b;
}
const inventory=new Container(36);let off;
const hunger={currentValue:10,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const saturation={currentValue:2,effectiveMax:20,setCurrentValue(v){this.currentValue=v}};
const player={id:'p1',selectedSlotIndex:0,isSneaking:false,location:{x:0,y:64,z:-1},dimension,effects:[],animations:[],messages:[],dp:new Map(),
 getGameMode(){return GameMode.Survival},
 getComponent(id){
  if(id==='minecraft:inventory')return {container:inventory};
  if(id==='minecraft:equippable')return {getEquipment:s=>s===EquipmentSlot.Offhand?off:undefined,setEquipment(s,v){if(s===EquipmentSlot.Offhand)off=v;return true}};
  if(id==='minecraft:player.hunger')return hunger;if(id==='minecraft:player.saturation')return saturation;
 },
 addEffect(id,duration,opt){this.effects.push({id,duration,opt})},
 playAnimation(id,opt){this.animations.push({id,opt,tick:system.currentTick})},
 setDynamicProperty(k,v){v===undefined?this.dp.delete(k):this.dp.set(k,v)},getDynamicProperty(k){return this.dp.get(k)},
 onScreenDisplay:{setActionBar(t){player.messages.push(t)}}};
const worldDP=new Map();
const world={afterEvents,beforeEvents,getAllPlayers:()=>[player],getDimension:id=>dimension,getDynamicProperty:k=>worldDP.get(k),setDynamicProperty(k,v){v===undefined?worldDP.delete(k):worldDP.set(k,v)}};
const enc=n=>n<0?'m'+Math.abs(n):'p'+n;
const stateKey=b=>'kaleidoscope_grilling:g_'+b.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(b.x)+'_'+enc(b.y)+'_'+enc(b.z);
const persisted=b=>JSON.parse(worldDP.get(stateKey(b)));
const intervals=[];
const system={currentTick:0,run(f){f()},runInterval(f,n){intervals.push({f,n})}};
function tick(n=1){for(let i=0;i<n;i++){system.currentTick++;for(const x of intervals)if(system.currentTick%x.n===0)x.f()}}
function hand(id,amount=1){inventory.setItem(0,id?new ItemStack(id,amount):undefined)}
function interact(block){const e={block,player,cancel:false};beforeEvents.playerInteractWithBlock.emit(e);return e}
function place(block){afterEvents.playerPlaceBlock.emit({block,player})}
function breakBlock(block){const e={block,player,cancel:false};beforeEvents.playerBreakBlock.emit(e);return e}

const ctx=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Error,Boolean,Math});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const files=['main.js','data.js','core_logic.js'];
const modules={};
for(const n of files)modules[n]=new vm.SourceTextModule(fs.readFileSync(new URL(n,root),'utf8'),{context:ctx,identifier:n});
const server=new vm.SyntheticModule(['world','system','ItemStack','EquipmentSlot','GameMode'],function(){this.setExport('world',world);this.setExport('system',system);this.setExport('ItemStack',ItemStack);this.setExport('EquipmentSlot',EquipmentSlot);this.setExport('GameMode',GameMode)},{context:ctx,identifier:'server'});
async function linker(spec){if(spec==='@minecraft/server')return server;return modules[spec.replace('./','')]}
await modules['main.js'].link(linker);await modules['main.js'].evaluate();

const a=makeBlock(0);place(a);
check('placement registers and creates 3-slot grill',()=>{assert.equal(a._c.slots.length,3);assert.equal(persisted(a).phase,0);assert.match(worldDP.get('kaleidoscope_grilling:a2_grills'),/"x":0/)});
hand('minecraft:flint_and_steel');check('flint and steel lights grill',()=>{const e=interact(a);assert.equal(e.cancel,true);assert.equal(persisted(a).lit,true)});
for(const id of ['raw_beef_skewer','raw_fish_skewer','raw_lamb_skewer']){hand('kaleidoscope_grilling:'+id);interact(a)}
check('three real container slots accept three raw skewers',()=>assert.deepEqual(a._c.slots.map(x=>x?.typeId),['kaleidoscope_grilling:raw_beef_skewer','kaleidoscope_grilling:raw_fish_skewer','kaleidoscope_grilling:raw_lamb_skewer']));
hand('kaleidoscope_grilling:canola_oil_brush');interact(a);
check('brush enters phase1 and stores heat',()=>{assert.equal(persisted(a).phase,1);assert.equal(persisted(a).heatTicks,1200)});
hand();
for(let i=1;i<=4;i++){interact(a);check('flip '+i,()=>assert.equal(persisted(a).flips,i));if(i<4)tick(20)}
check('four flips reach phase2',()=>assert.equal(persisted(a).phase,2));
hand('kaleidoscope_grilling:special_seasoning');interact(a);
check('seasoning unlocks extraction',()=>assert.equal(persisted(a).seasoned,true));
hand();player.isSneaking=true;interact(a);player.isSneaking=false;
check('shift empty-hand extracts all as matching cooked items',()=>{
 const got=inventory.slots.filter(x=>x?.typeId?.startsWith('kaleidoscope_grilling:grilled_')).map(x=>x.typeId).sort();
 assert.deepEqual(got,['kaleidoscope_grilling:grilled_beef_skewer','kaleidoscope_grilling:grilled_fish_skewer','kaleidoscope_grilling:grilled_lamb_skewer'].sort());
 assert.equal(a._c.slots.filter(Boolean).length,0);assert.equal(persisted(a).phase,0);
});
const dark=makeBlock(2);place(dark);hand('minecraft:flint_and_steel');interact(dark);hand('kaleidoscope_grilling:raw_beef_skewer');interact(dark);hand('kaleidoscope_grilling:canola_oil_brush');interact(dark);hand();tick(800);
check('800 lit occupied ticks become overcooked phase3',()=>assert.equal(persisted(dark).phase,3));
interact(dark);
check('phase3 extraction is dark grilling',()=>assert.ok(inventory.slots.some(x=>x?.typeId==='kaleidoscope_grilling:dark_grilling')));
const burnt=makeBlock(4);place(burnt);hand('minecraft:flint_and_steel');interact(burnt);hand('kaleidoscope_grilling:raw_fish_skewer');interact(burnt);hand('kaleidoscope_grilling:canola_oil_brush');interact(burnt);hand();tick(1200);
check('800+400 ticks eject charcoal and clear slots',()=>{assert.ok(drops.some(x=>x.stack.typeId==='minecraft:charcoal'));assert.equal(burnt._c.slots.filter(Boolean).length,0);assert.equal(persisted(burnt).phase,0)});
const partial=makeBlock(6);place(partial);hand('minecraft:flint_and_steel');interact(partial);hand('kaleidoscope_grilling:raw_beef_skewer');interact(partial);hand('kaleidoscope_grilling:canola_oil_brush');interact(partial);
check('breaking partial process is intercepted',()=>assert.equal(breakBlock(partial).cancel,true));
check('partial break produces mysterious skewer',()=>assert.ok(drops.some(x=>x.stack.typeId==='kaleidoscope_grilling:mysterious_skewer')));
hand('kaleidoscope_grilling:grilled_beef_skewer');hunger.currentValue=10;saturation.currentValue=2;
afterEvents.itemStartUse.emit({source:player,itemStack:inventory.getItem(0)});tick(25);afterEvents.itemStopUse.emit({source:player,itemStack:inventory.getItem(0)});
check('25 tick early release settles real hunger and saturation',()=>{assert.equal(hunger.currentValue,15);assert.equal(saturation.currentValue,8);assert.equal(inventory.getItem(0),undefined)});
check('early grilled beef applies exact vanilla strength effect',()=>assert.ok(player.effects.some(x=>x.id==='strength'&&x.duration===200)));
check('A1.16 FOUR player animation is reused for formal beef item',()=>assert.ok(player.animations.some(x=>x.id==='animation.kg_imm.player.eat_four.main')));
console.log(JSON.stringify({passed:checks,failed:0,scope:'generated A2 runtime in mock BlockEntity/inventory/event host; not Minecraft/BDS engine acceptance'}));
