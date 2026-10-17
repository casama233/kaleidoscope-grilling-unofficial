import {normalizePublicFood} from './host_api/food_api_core.js';
const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
export const COOKERY_OUTPUT_READY_EVENT='kaleidoscope_grilling:cookery_output_ready';

function coord(value){const n=Number(value);return Number.isFinite(n)?Math.floor(n):null}
function slot(value){const n=Number(value);return Number.isInteger(n)&&n>=0&&n<256?n:null}
function amount(value){const n=Number(value);return Number.isInteger(n)&&n>0&&n<=64?n:null}
function dimension(value){return typeof value==='string'&&value.length>0&&value.length<=128?value:''}

export function normalizeCookeryOutputRequest(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
 const version=Number(raw.version??1);if(version!==1&&version!==2)return null;
 const metadata=version===2?normalizePublicFood(raw.metadata):undefined;
 if(version===2&&(!metadata||typeof raw.receiptId!=='string'||!raw.receiptId||raw.receiptId.length>512))return null;
 const extra=version===2?{receiptId:raw.receiptId,metadata}:{};
 const station=raw.station??{},sx=coord(station.x),sy=coord(station.y),sz=coord(station.z),sd=dimension(station.dimensionId);
 if(!sd||sx===null||sy===null||sz===null)return null;
 const target=raw.target??{},kind=String(target.kind??''),targetSlot=slot(target.slot);
 const expectedId=String(target.expectedId??''),expectedAmount=amount(target.expectedAmount);
 if(!['player_slot','block_slot','item_entity'].includes(kind)||kind!=='item_entity'&&targetSlot===null||!ITEM_ID.test(expectedId)||expectedAmount===null)return null;
 if(kind==='item_entity'){const entityId=String(target.entityId??'');if(version!==2||!entityId||entityId.length>256)return null;return {version,...extra,station:{dimensionId:sd,x:sx,y:sy,z:sz},target:{kind,entityId,expectedId,expectedAmount}};}
 if(kind==='player_slot'){
  const playerId=String(target.playerId??'');if(!playerId||playerId.length>256)return null;
  return {version,...extra,station:{dimensionId:sd,x:sx,y:sy,z:sz},
   target:{kind,playerId,slot:targetSlot,expectedId,expectedAmount}};
 }
 const td=dimension(target.dimensionId),tx=coord(target.x),ty=coord(target.y),tz=coord(target.z);
 if(!td||tx===null||ty===null||tz===null)return null;
 return {version,...extra,station:{dimensionId:sd,x:sx,y:sy,z:sz},
  target:{kind,dimensionId:td,x:tx,y:ty,z:tz,slot:targetSlot,expectedId,expectedAmount}};
}

export function authoritativeTargetMatches(stack,target){
 return !!stack&&!!target&&stack.typeId===target.expectedId&&Number(stack.amount)===target.expectedAmount;
}
