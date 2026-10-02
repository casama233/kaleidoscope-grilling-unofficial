import {world,system,CommandPermissionLevel,CustomCommandParamType,CustomCommandStatus} from '@minecraft/server';
import {normalizeConfig,configValue} from './server_config_core.js';
const KEY='kaleidoscope_grilling:server_config_v1';let cache;
export function grillingConfig(){if(!cache){let v;try{v=JSON.parse(world.getDynamicProperty(KEY)??'{}')}catch{}cache=normalizeConfig(v)}return cache;}
export function setGrillingConfig(key,value){const next={...grillingConfig(),[key]:configValue(key,value)};world.setDynamicProperty(KEY,JSON.stringify(next));cache=next;return next;}
system.beforeEvents.startup.subscribe(({customCommandRegistry})=>{
 customCommandRegistry.registerCommand({name:'kaleidoscope_grilling:config',description:'Set Grilling server option (saturationMultiplier, fullHungerEating, graphicalEatingHud, contentsHelpers, fixedGrillHelpers, placedHelpers, contentsTargetsPerTick)',permissionLevel:CommandPermissionLevel.GameDirectors,cheatsRequired:false,mandatoryParameters:[{name:'key',type:CustomCommandParamType.String},{name:'value',type:CustomCommandParamType.String}]},(origin,key,value)=>{
  try{configValue(key,value)}catch(error){return {status:CustomCommandStatus.Failure,message:String(error)}}
  system.run(()=>{try{setGrillingConfig(key,value);origin.sourceEntity?.sendMessage('Grilling '+key+' = '+value)}catch(error){console.warn('[Grilling configuration] '+error)}});
  return {status:CustomCommandStatus.Success};
 });
});
