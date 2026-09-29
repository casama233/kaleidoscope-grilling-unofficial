const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
export const COOKERY_OUTPUT_READY_EVENT='kaleidoscope_grilling:cookery_output_ready';

function coord(value){const n=Number(value);return Number.isFinite(n)?Math.floor(n):null}
function slot(value){const n=Number(value);return Number.isInteger(n)&&n>=0&&n<256?n:null}
function amount(value){const n=Number(value);return Number.isInteger(n)&&n>0&&n<=64?n:null}
function dimension(value){return typeof value==='string'&&value.length>0&&value.length<=128?value:''}

export function normalizeCookeryOutputRequest(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
 const version=Number(raw.version??1);if(version!==1)return null;
 const station=raw.station??{},sx=coord(station.x),sy=coord(station.y),sz=coord(station.z),sd=dimension(station.dimensionId);
 if(!sd||sx===null||sy===null||sz===null)return null;
 const target=raw.target??{},kind=String(target.kind??''),targetSlot=slot(target.slot);
 const expectedId=String(target.expectedId??''),expectedAmount=amount(target.expectedAmount);
 if(!['player_slot','block_slot'].includes(kind)||targetSlot===null||!ITEM_ID.test(expectedId)||expectedAmount===null)return null;
 if(kind==='player_slot'){
  const playerId=String(target.playerId??'');if(!playerId||playerId.length>256)return null;
  return {version:1,station:{dimensionId:sd,x:sx,y:sy,z:sz},
   target:{kind,playerId,slot:targetSlot,expectedId,expectedAmount}};
 }
 const td=dimension(target.dimensionId),tx=coord(target.x),ty=coord(target.y),tz=coord(target.z);
 if(!td||tx===null||ty===null||tz===null)return null;
 return {version:1,station:{dimensionId:sd,x:sx,y:sy,z:sz},
  target:{kind,dimensionId:td,x:tx,y:ty,z:tz,slot:targetSlot,expectedId,expectedAmount}};
}

export function authoritativeTargetMatches(stack,target){
 return !!stack&&!!target&&stack.typeId===target.expectedId&&Number(stack.amount)===target.expectedAmount;
}
