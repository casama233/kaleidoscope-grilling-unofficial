/** Java 1.1.1 AdvancedRackRenderer: upper containers belong to the spice-level
 * block mesh. Only the first three non-empty slots 5..8 occupy visible hooks.
 * Storage still has four tool slots; this is a read-only display projection.
 */
export const ADVANCED_RACK_HOOK_X=Object.freeze([-.284,0,.278]);
export function advancedRackToolVisuals(readItem){
 const rows=[];
 for(let slot=5;slot<9&&rows.length<ADVANCED_RACK_HOOK_X.length;slot++){
  const stack=readItem(slot);
  if(stack)rows.push({slot,hook:rows.length,x:ADVANCED_RACK_HOOK_X[rows.length],stack});
 }
 return rows;
}
