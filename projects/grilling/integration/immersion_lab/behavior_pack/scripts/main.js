import {world,system} from '@minecraft/server';
import {initial,restore,nextAction,apply,advance,cancel,view} from './flow.js';
import {AUDIO} from './audio.js';
const TYPE='kg_imm:rehearsal',SAVE='kg_imm:rehearsal_state';
const scenes=new Map(),listeners=new Map(),warned=new Set();
const ACTIONS={ignite:'點火',insert:'放入三串（展示樣本）',brush:'刷油',flip:'翻面',season:'撒料',take:'取串',eat:'四口進食展示',reset:'重置'};
function warning(id,error){if(!warned.has(id)){warned.add(id);console.warn(`[Grilling immersion] ${id}: ${String(error)}`);}}
function stop(p,id){try{p.runCommand(`stopsound @s kg_imm.${id}`);}catch(e){warning('stop-sound',e);}}
function mutedPlayer(p){stop(p,'grill_loop');for(let i=0;i<8;i++)stop(p,'four_skewer_eat_ch'+i);}
function watch(entity){
 if(entity.typeId!==TYPE||scenes.has(entity.id)||scenes.size>=8)return;
 try{const state=restore(entity.getDynamicProperty(SAVE));const used=new Set([...scenes.values()].map(x=>x.channel));const channel=Array.from({length:8},(_,i)=>i).find(i=>!used.has(i));scenes.set(entity.id,{entity,state,properties:new Map(),lastTap:-10,channel});sync(scenes.get(entity.id),system.currentTick);}catch(e){warning(entity.id,e);}
}
function property(row,name,value){if(row.properties.get(name)!==value){row.entity.setProperty(`kg_imm:${name}`,value);row.properties.set(name,value);}}
function sync(row,tick){const v=view(row.state,tick);for(const [k,x] of Object.entries(v))if(k!=='loop')property(row,k,k==='action'?({idle:0,brush:1,flip:2,season:3,eat:4})[x]:x);property(row,'serial',row.state.seq%1000000);}
function save(row){row.entity.setDynamicProperty(SAVE,JSON.stringify(row.state));}
function nearPlayers(entity,radius=24){return world.getAllPlayers().filter(p=>{try{return p.dimension.id===entity.dimension.id&&Math.hypot(p.location.x-entity.location.x,p.location.y-entity.location.y,p.location.z-entity.location.z)<=radius;}catch{return false;}});}
function sound(row,id,volume=1){for(const p of nearPlayers(row.entity))try{p.playSound(`kg_imm.${id}`,{location:row.entity.location,volume,pitch:1});}catch(e){warning('audio-'+id,e);}}
function events(row,ev){for(const e of ev){
 if(e.kind==='ignite') {try{row.entity.dimension.playSound('fire.ignite',row.entity.location);}catch(x){warning('ignite-sound',x);}}
 if(e.kind==='insert'||e.kind==='take')sound(row,'pickup_item',.8);
 if(e.kind==='brush'||e.kind==='flip')sound(row,'grill_flip',e.kind==='brush'?.75:1);
 if(e.kind==='season')sound(row,'season',.85);
 if(e.kind==='eat_start')sound(row,'four_skewer_eat_ch'+row.channel);
 if(e.kind==='stop_audio'||(e.kind==='action_end'&&e.action==='eat'))for(const p of world.getAllPlayers())stop(p,'four_skewer_eat_ch'+row.channel);
}}
world.afterEvents.entitySpawn.subscribe(e=>watch(e.entity));
world.afterEvents.playerInteractWithEntity.subscribe(e=>{
 if(e.target.typeId!==TYPE || e.beforeItemStack!==undefined || e.itemStack!==undefined)return;watch(e.target);const row=scenes.get(e.target.id);if(!row)return;
 const now=system.currentTick;if(now-row.lastTap<3)return;row.lastTap=now;
 try{
  if(e.player.isSneaking){const r=cancel(row.state);row.state=row.state.action?r.state:{...initial(),seq:row.state.seq+1};events(row,r.events);save(row);sync(row,now);e.player.onScreenDisplay.setActionBar('動作已取消或驗收台已重置；不扣材料、不回復飢餓');return;}
  const action=nextAction(row.state);const r=apply(row.state,action,now);if(!r.accepted)return;
  row.state=r.state;
  if(action==='flip')for(let i=0;i<3;i++)property(row,'height'+i,.28+Math.random()*.1);
  save(row);sync(row,now);events(row,r.events);
  e.player.onScreenDisplay.setActionBar(`煙火動效驗收｜${ACTIONS[action]}｜蹲下互動可取消`);
 }catch(x){warning(row.entity.id,x);}
});
function discover(){for(const dim of ['overworld','nether','the_end'])try{for(const e of world.getDimension(dim).getEntities({type:TYPE}))watch(e);}catch(x){warning('discover-'+dim,x);}}
system.run(discover);system.runInterval(discover,40);
system.runInterval(()=>{
 const now=system.currentTick,active=[];
 for(const [id,row] of scenes){try{
  if(!row.entity.isValid)throw new Error("Entity unloaded or removed");
  const before=row.state;const r=advance(before,now);row.state=r.state;if(r.events.length){save(row);events(row,r.events);}sync(row,now);
  const v=view(row.state,now);if(v.loop)active.push(row);
  // Original Java animateTick smoke/flame probabilities and local ranges. Built-in Bedrock emitters are an explicit visual approximation.
  if(v.lit&&nearPlayers(row.entity,24).length){const p=row.entity.location;
   if(Math.random()<1/3)row.entity.dimension.spawnParticle('minecraft:basic_smoke_particle',{x:p.x+(Math.random()-.5)*.5,y:p.y+.22,z:p.z+(Math.random()-.5)*.5});
   if(Math.random()<1/8)row.entity.dimension.spawnParticle('minecraft:basic_flame_particle',{x:p.x+(Math.random()-.5)*.4,y:p.y+.18,z:p.z+(Math.random()-.5)*.4});
  }
 }catch(x){for(const p of world.getAllPlayers())stop(p,'four_skewer_eat_ch'+row.channel);scenes.delete(id);warning(id,x);}}
 // One nearest-grill sound per listener: no volume multiplication or one loop instance per game tick.
 for(const p of world.getAllPlayers())try{
  let nearest=null,distance=24;
  for(const row of active){const e=row.entity;if(e.dimension.id!==p.dimension.id)continue;const d=Math.hypot(e.location.x-p.location.x,e.location.y-p.location.y,e.location.z-p.location.z);if(d<distance){distance=d;nearest=row;}}
  const previous=listeners.get(p.id);
  if(!nearest){if(previous){stop(p,'grill_loop');listeners.delete(p.id);}continue;}
  if(!previous||previous.scene!==nearest.entity.id){stop(p,'grill_loop');listeners.set(p.id,{scene:nearest.entity.id,next:0});}
  const slot=listeners.get(p.id);if(now>=slot.next){p.playSound('kg_imm.grill_loop',{location:nearest.entity.location,volume:.65,pitch:1});slot.next=now+Math.max(1,Math.ceil(AUDIO.grill_loop.duration*20));}
 }catch(x){warning('listener',x);}
 const ids=new Set(world.getAllPlayers().map(p=>p.id));for(const id of listeners.keys())if(!ids.has(id))listeners.delete(id);
},1);
world.afterEvents.playerSpawn.subscribe(e=>{if(e.initialSpawn)mutedPlayer(e.player);});
