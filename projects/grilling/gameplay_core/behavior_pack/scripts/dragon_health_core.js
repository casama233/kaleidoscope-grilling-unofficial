/** Native health boost supplies 4/8 HP; a bounded 2 HP ledger supplies the remainder. */
export function planDragonDamage(pool,damage,pending=0){
 const available=Math.max(0,Math.min(2,Number(pool)||0)-Math.max(0,Number(pending)||0)),incoming=Math.max(0,Number(damage)||0),absorbed=Math.min(available,incoming);
 return {absorbed,remaining:incoming-absorbed,available:available-absorbed,pending:pending+absorbed};
}
export function dragonHealthGain(previousAmplifier,nextAmplifier){
 const old=previousAmplifier===undefined?0:previousAmplifier>0?8:4,next=nextAmplifier>0?8:4;
 return Math.max(0,next-old);
}
