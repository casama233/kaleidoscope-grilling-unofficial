import {RACK_TOOL_X} from './advanced_rack_layout.js';
/** Owner-requested no-menu adaptation: each saved tool slot has its own hook.
 * Unlike Java's three occupied-item hooks, empty neighbors never move a tool.
 * This is a read-only projection; helpers never own rack contents.
 */
export const ADVANCED_RACK_HOOK_X=RACK_TOOL_X;
export function advancedRackToolVisuals(readItem){
 const rows=[];
 for(let slot=5;slot<9;slot++){
  const stack=readItem(slot);
  if(stack)rows.push({slot,hook:slot-5,x:ADVANCED_RACK_HOOK_X[slot-5],stack});
 }
 return rows;
}
