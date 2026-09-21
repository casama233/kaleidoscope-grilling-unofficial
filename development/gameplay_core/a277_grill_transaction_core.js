export function commitTwoParty(applyPrimary,applySecondary,rollbackPrimary,rollbackSecondary){
 try{
  applyPrimary();
  applySecondary();
  return {ok:true,rollbackErrors:0};
 }catch(error){
  let rollbackErrors=0;
  try{rollbackSecondary()}catch{rollbackErrors++}
  try{rollbackPrimary()}catch{rollbackErrors++}
  return {ok:false,error,rollbackErrors};
 }
}

export function chooseExtractDelivery(emptySlot){
 return Number.isInteger(emptySlot)&&emptySlot>=0?{kind:'inventory',slot:emptySlot}:{kind:'spawn',slot:-1};
}

export function breakEscrowDropCount(rawCount,creative){
 const n=Math.max(0,Math.min(3,Math.floor(Number(rawCount)||0)));
 return n+(creative?0:1);
}

export function shouldResetAfterExtract(remaining){
 return Math.max(0,Math.floor(Number(remaining)||0))===0;
}
