// Synchronous snapshot ownership for the existing plant journal. The caller
// supplies native full-stack/permutation comparison; these helpers never infer
// ownership from an item ID, count, visible lore, or a successful void setter.
export function createOwnedPlantWrite({read,write,same,before,after,acceptPlannedAfter=false}){
 let entered=false,attempted=false;
 return {
  apply(){
   entered=true;
   const current=read();
   if(!same(current,before)&&!(acceptPlannedAfter&&same(current,after)))throw Error('Plant write preimage changed');
   attempted=true;
   write(after);
   if(!same(read(),after))throw Error('Plant write was not acknowledged');
  },
  rollback(){
   if(!entered)return;
   // A precondition/read failure did not establish ownership. In particular,
   // a coincidentally matching debit must not be refunded as our own write.
   if(!attempted)throw Error('Plant write ownership unavailable');
   const current=read();
   if(same(current,before))return;
   if(!same(current,after))throw Error('Plant rollback ownership changed');
   let failure;
   try{write(before)}catch(error){failure=error}
   // A native setter can complete before throwing. Only the exact readback
   // proves restoration; a silent no-op or another value remains unresolved.
   if(!same(read(),before))throw failure??Error('Plant rollback was not acknowledged');
  }
 };
}

export function plantFertilizerSteps(debit,mutations){
 if(!debit)return mutations;
 let refundAllowed=true;
 return [{
  apply:()=>debit.apply(),
  rollback(){
   // commitSteps continues its reverse walk after a rollback error. Keep the
   // already paid cost when any plant/drop outcome has not been restored.
   if(!refundAllowed)throw Error('Plant fertilizer cost retained for recovery');
   return debit.rollback();
  }
 },...mutations.map(step=>({
  apply:()=>step.apply(),
  rollback(){
   try{
    const restored=step.rollback();
    if(restored===false)throw Error('Plant mutation rollback rejected');
    return restored;
   }catch(error){refundAllowed=false;throw error}
  }
 }))];
}
