import {world} from '@minecraft/server';
import {initialState,normalizeState} from './core_logic.js';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}

export function grillStateKey(block){
 return 'kaleidoscope_grilling:g_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z);
}

export function readGrillState(block){
 const raw=world.getDynamicProperty(grillStateKey(block));
 if(raw===undefined)return initialState();
 if(typeof raw!=='string')throw new Error('invalid persisted grill state');
 return normalizeState(JSON.parse(raw));
}

export function occupiedGrillSlots(block){
 const c=block?.getComponent('minecraft:inventory')?.container;
 if(!c)return 0;
 let n=0;
 for(let i=0;i<3;i++)if(c.getItem(i))n++;
 return n;
}
