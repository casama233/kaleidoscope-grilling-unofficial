import {world,system} from '@minecraft/server';
import {
 CROSSHAIR_HUD_POLL_TICKS,CROSSHAIR_HUD_MAX_DISTANCE,normalizeHudResult,shouldPublishHud
} from './a2739_crosshair_hud_core.js';

const PROVIDERS=[];
const LAST_SIGNATURE=new Map();

export function registerCrosshairHudProvider({id,priority=0,probe}={}){
 if(!id||typeof probe!=='function')return false;
 if(PROVIDERS.some(x=>x.id===id))return false;
 PROVIDERS.push({id:String(id),priority:Number(priority)||0,probe});
 PROVIDERS.sort((a,b)=>b.priority-a.priority);
 return true;
}

function queryHud(player,block){
 if(!block)return undefined;
 for(const provider of PROVIDERS){
  try{
   const normalized=normalizeHudResult(provider.id,provider.probe(player,block));
   if(normalized)return normalized;
  }catch{}
 }
 return undefined;
}

system.runInterval(()=>{
 const live=new Set();
 for(const player of world.getPlayers()){
  live.add(player.id);
  let block;
  try{
   block=player.getBlockFromViewDirection({
    maxDistance:CROSSHAIR_HUD_MAX_DISTANCE,
    includeLiquidBlocks:false,
    includePassableBlocks:false
   })?.block;
  }catch{}
  const result=queryHud(player,block);
  if(!result){LAST_SIGNATURE.delete(player.id);continue}
  const previous=LAST_SIGNATURE.get(player.id);
  if(!shouldPublishHud(previous,result.signature))continue;
  try{
   player.onScreenDisplay.setActionBar(result.message);
   LAST_SIGNATURE.set(player.id,result.signature);
  }catch{}
 }
 for(const id of [...LAST_SIGNATURE.keys()])if(!live.has(id))LAST_SIGNATURE.delete(id);
},CROSSHAIR_HUD_POLL_TICKS);
