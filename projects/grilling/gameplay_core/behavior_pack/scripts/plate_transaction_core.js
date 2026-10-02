import {commitSteps} from './a277_grill_transaction_core.js';

/** Do not silently turn damaged/unsupported saved contents into an empty plate. */
export function decodePlateStorage(raw){
 if(raw===undefined)return [];
 if(typeof raw!=='string')throw Error('Grilling: unreadable plate storage');
 const rows=JSON.parse(raw);
 if(!Array.isArray(rows)||rows.length>5||rows.some(row=>
  !row||typeof row.id!=='string'||!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(row.id)||
  (row.native&&(row.native.version!==1||row.native.id!==row.id))))
  throw Error('Grilling: invalid plate storage; recovery required');
 return rows;
}

/** The bound reader/writer must refer to the same captured slot/property. */
export function verifiedPlateStep({read,write,before,after,signature=JSON.stringify}){
 const expectedBefore=signature(before),expectedAfter=signature(after);
 let attempted=false;
 function put(value,expected){
  if(write(value)===false||signature(read())!==expected)throw Error('Grilling: plate write rejected');
 }
 return {
  apply(){if(signature(read())!==expectedBefore)throw Error('Grilling: plate input changed');attempted=true;put(after,expectedAfter)},
  rollback(){if(attempted)put(before,expectedBefore)}
 };
}

/** Synchronous rollback only. Ambiguous ownership must block further transfers. */
export function commitPlateSteps(steps,quarantine){
 const result=commitSteps(steps);
 if(!result.ok&&result.rollbackErrors){
  quarantine('plate transaction rollback incomplete');
  throw Error('Grilling: plate transaction recovery required');
 }
 return result;
}

// Java SkewerPlatePlacement uses Player.getDirection(), without getOpposite().
export function plateFacingFromYaw(yaw){
 if(!Number.isFinite(yaw))throw Error('Grilling: plate facing unavailable');
 return ['south','west','north','east'][((Math.floor(yaw/90+.5)%4)+4)%4];
}
