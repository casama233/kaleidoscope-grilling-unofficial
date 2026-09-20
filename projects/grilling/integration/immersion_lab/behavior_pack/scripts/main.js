import {world,system} from '@minecraft/server';
import {initial,restore,nextAction,apply,advance,cancel,view} from './flow.js';
import {AUDIO} from './audio.js';
import {SELECTORS,resolveProfile} from './profile_rules.js';
import {selector,tool,stance,beginEat,bite,finishEat,recover,playTool,playReach} from './player_binding.js';

const TYPE='kg_imm:rehearsal',SAVE='kg_imm:rehearsal_state';
const scenes=new Map(),listeners=new Map(),warned=new Set();
const ACTIONS={ignite:'點火',insert:'放入三串（展示樣本）',brush:'刷油',flip:'翻面',season:'撒料',take:'取串',eat:'依手持測試串套用原作進食規則',reset:'重置'};

function warning(id,error){if(!warned.has(id)){warned.add(id);console.warn('[Grilling immersion] '+id+': '+String(error));}}
function stop(p,id){try{p.runCommand('stopsound @s kg_imm.'+id);}catch(e){warning('stop-sound',e);}}
function mutedPlayer(p){
 stop(p,'grill_loop');
 for(const id of ['one_skewer_eat','two_skewer_eat','three_skewer_eat','four_skewer_eat'])stop(p,id);
 for(let i=0;i<8;i++)stop(p,'four_skewer_eat_ch'+i);
}
function watch(entity){
 if(entity.typeId!==TYPE||scenes.has(entity.id)||scenes.size>=8)return;
 try{
  const state=restore(entity.getDynamicProperty(SAVE));
  const used=new Set([...scenes.values()].map(x=>x.channel));
  const channel=Array.from({length:8},(_,i)=>i).find(i=>!used.has(i));
  scenes.set(entity.id,{entity,state,properties:new Map(),lastTap:-10,channel,performer:null});
  sync(scenes.get(entity.id),system.currentTick);
 }catch(e){warning(entity.id,e);}
}
function property(row,name,value){
 if(row.properties.get(name)!==value){row.entity.setProperty('kg_imm:'+name,value);row.properties.set(name,value);}
}
function sync(row,tick){
 const v=view(row.state,tick);
 for(const [k,x] of Object.entries(v)){
  if(k==='loop'||k==='profile')continue;
  property(row,k,k==='action'?({idle:0,brush:1,flip:2,season:3,eat:4})[x]:x);
 }
 property(row,'serial',row.state.seq%1000000);
}
function save(row){row.entity.setDynamicProperty(SAVE,JSON.stringify(row.state));}
function nearPlayers(entity,radius=24){
 return world.getAllPlayers().filter(p=>{
  try{return p.dimension.id===entity.dimension.id&&Math.hypot(p.location.x-entity.location.x,p.location.y-entity.location.y,p.location.z-entity.location.z)<=radius;}
  catch{return false;}
 });
}
function sound(row,id,volume=1){for(const p of nearPlayers(row.entity))try{p.playSound('kg_imm.'+id,{location:row.entity.location,volume,pitch:1});}catch(e){warning('audio-'+id,e);}}
function performerPlayer(row){return row.performer?world.getAllPlayers().find(p=>p.id===row.performer.playerId):undefined;}
function endPerformer(row){
 const p=performerPlayer(row);
 if(p)finishEat(p,row.performer);
 row.performer=null;
}
function events(row,ev){
 for(const e of ev){
  if(e.kind==='ignite'){try{row.entity.dimension.playSound('fire.ignite',row.entity.location);}catch(x){warning('ignite-sound',x);}}
  if(e.kind==='insert'||e.kind==='take')sound(row,'pickup_item',.8);
  if(e.kind==='flip')sound(row,'grill_flip',1);
  if(e.kind==='brush_start')sound(row,'pickup_item',.45);
  if(e.kind==='brush_contact')sound(row,'grill_flip',.75);
  if(e.kind==='season_start')sound(row,'shake_seasoning',.72);
  if(e.kind==='season_contact')sound(row,'season',.85);
  if(e.kind==='bite'&&row.performer){
   const p=performerPlayer(row);
   if(!p||!bite(p,row.performer,e.index)){
    if(p)finishEat(p,row.performer);
    row.performer=null;
    const c=cancel(row.state);row.state=c.state;save(row);sync(row,system.currentTick);
   }
  }
  if(e.kind==='action_end'&&e.action==='eat')endPerformer(row);
  if(e.kind==='stop_audio'&&row.performer)endPerformer(row);
 }
}
world.afterEvents.entitySpawn.subscribe(e=>watch(e.entity));
world.afterEvents.playerInteractWithEntity.subscribe(e=>{
 if(e.target.typeId!==TYPE)return;
 watch(e.target);const row=scenes.get(e.target.id);if(!row)return;
 const now=system.currentTick;
 try{
  if(e.player.isSneaking){
   row.lastTap=now;
   endPerformer(row);
   const r=cancel(row.state);
   row.state=row.state.action?r.state:{...initial(),seq:row.state.seq+1};
   events(row,r.events);save(row);sync(row,now);
   e.player.onScreenDisplay.setActionBar('動作已取消或驗收台已重置；不扣材料、不回復飢餓');
   return;
  }
  if(now-row.lastTap<3)return;row.lastTap=now;
  const action=nextAction(row.state);let hand=null,profile=null;
  if(action==='brush'){
   hand=tool(e.player,'kg_imm:oil_brush');
   if(!hand||!stance(e.player,row.entity)){e.player.onScreenDisplay.setActionBar('請手持驗收刷具，站在0.72–1.32格並面向爐心再刷油');return;}
   playTool(e.player,'brush',hand);
  }else if(action==='season'){
   hand=tool(e.player,'kg_imm:seasoning_bottle');
   if(!hand||!stance(e.player,row.entity)){e.player.onScreenDisplay.setActionBar('請手持驗收調料瓶，站在0.72–1.32格並面向爐心再撒料');return;}
   playTool(e.player,'season',hand);
  }else if(action==='eat'){
   hand=selector(e.player);
   if(!hand){e.player.onScreenDisplay.setActionBar('請主手或副手拿 ONE / TWO / THREE / THREE_ALT / THREE_RANDOM / FOUR 任一驗收串');return;}
   profile=resolveProfile(SELECTORS[hand.item.typeId],Math.random());
  }else if(action==='insert'||action==='take'){
   playReach(e.player,'main');
  }
  const before=row.state;
  const r=apply(row.state,action,now,profile?{profile}:{});
  if(!r.accepted)return;
  row.state=r.state;
  if(action==='eat'){
   try{row.performer=beginEat(e.player,hand,profile);}
   catch(x){row.state=before;throw x;}
  }
  if(action==='flip')for(let i=0;i<3;i++)property(row,'height'+i,.28+Math.random()*.1);
  save(row);sync(row,now);events(row,r.events);
  e.player.onScreenDisplay.setActionBar('煙火沉浸驗收｜'+ACTIONS[action]+(profile?' → '+profile:'')+'｜蹲下互動可取消');
 }catch(x){warning(row.entity.id,x);}
});
function discover(){
 for(const dim of ['overworld','nether','the_end'])try{for(const e of world.getDimension(dim).getEntities({type:TYPE}))watch(e);}catch(x){warning('discover-'+dim,x);}
}
system.run(discover);system.runInterval(discover,40);
system.runInterval(()=>{
 const now=system.currentTick,active=[];
 for(const [id,row] of scenes){
  try{
   if(!row.entity.isValid)throw new Error('Entity unloaded or removed');
   if(row.performer&&!performerPlayer(row)){
    const c=cancel(row.state);row.state=c.state;row.performer=null;save(row);sync(row,now);
   }
   const r=advance(row.state,now);row.state=r.state;
   if(r.events.length){save(row);events(row,r.events);}
   sync(row,now);
   const v=view(row.state,now);if(v.loop)active.push(row);
   if(v.lit&&nearPlayers(row.entity,24).length){
    const p=row.entity.location;
    if(Math.random()<1/3)row.entity.dimension.spawnParticle('minecraft:basic_smoke_particle',{x:p.x+(Math.random()-.5)*.5,y:p.y+.22,z:p.z+(Math.random()-.5)*.5});
    if(Math.random()<1/8)row.entity.dimension.spawnParticle('minecraft:basic_flame_particle',{x:p.x+(Math.random()-.5)*.4,y:p.y+.18,z:p.z+(Math.random()-.5)*.4});
   }
  }catch(x){
   endPerformer(row);scenes.delete(id);warning(id,x);
  }
 }
 for(const p of world.getAllPlayers()){
  try{
   let nearest=null,distance=24;
   for(const row of active){
    const e=row.entity;if(e.dimension.id!==p.dimension.id)continue;
    const d=Math.hypot(e.location.x-p.location.x,e.location.y-p.location.y,e.location.z-p.location.z);
    if(d<distance){distance=d;nearest=row;}
   }
   const previous=listeners.get(p.id);
   if(!nearest){if(previous){stop(p,'grill_loop');listeners.delete(p.id);}continue;}
   if(!previous||previous.scene!==nearest.entity.id){stop(p,'grill_loop');listeners.set(p.id,{scene:nearest.entity.id,next:0});}
   const slot=listeners.get(p.id);
   if(now>=slot.next){p.playSound('kg_imm.grill_loop',{location:nearest.entity.location,volume:.65,pitch:1});slot.next=now+Math.max(1,Math.ceil(AUDIO.grill_loop.duration*20));}
  }catch(x){warning('listener',x);}
 }
 const ids=new Set(world.getAllPlayers().map(p=>p.id));for(const id of listeners.keys())if(!ids.has(id))listeners.delete(id);
},1);
world.afterEvents.playerSpawn.subscribe(e=>{if(e.initialSpawn){mutedPlayer(e.player);try{recover(e.player);}catch(x){warning('recover-'+e.player.id,x);}}});
